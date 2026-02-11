import os
import sys
import time
from logging import getLogger
from textwrap import dedent
from typing import Any, BinaryIO, Callable, Dict, Optional

try:
    from minny.bare_metal_target import BareMetalTargetManager
    from minny.connection import MicroPythonConnection
    from minny.target import ManagementError
    MINNY_AVAILABLE = True
except ImportError:
    try:
        # Compatibility layer for different minny version
        from minny.bare_metal import SerialPortAdapter, BareMetalAdapter
        from minny.connection import MicroPythonConnection
        from minny.common import ManagementError
        
        class BareMetalTargetManager(SerialPortAdapter):
            def __init__(self, connection, clean, **kwargs):
                self._clean = clean
                self._cwd = kwargs.get("cwd")
                super().__init__(
                    connection,
                    submit_mode=kwargs.get("submit_mode"),
                    write_block_size=kwargs.get("write_block_size"),
                    write_block_delay=kwargs.get("write_block_delay"),
                )

            def launch_main_program(self):
                # Send soft reboot command (CTRL-D)
                try:
                    self._write(b"\x04")
                except:
                    pass
            
            def get_cwd(self):
                if not self._cwd:
                    try:
                        self._cwd = self._evaluate("__minny_helper.os.getcwd()")
                    except:
                        self._cwd = "/"
                return self._cwd
                
            def cd(self, path):
                self._evaluate("__minny_helper.os.chdir(%r)" % path)
                self._cwd = self._evaluate("__minny_helper.os.getcwd()")

            def mkdir(self, path):
                self._evaluate("__minny_helper.os.mkdir(%r)" % path)

            def rmdir(self, path):
                self._evaluate("__minny_helper.os.rmdir(%r)" % path)

            def _get_interpreter_kind(self):
                return "MicroPython"

            def _using_simplified_micropython(self):
                # Assume standard MicroPython for now
                return False

            def _prepare_disconnect(self):
                pass
            
            def _get_stat_mode(self, path):
                stat = self.try_get_stat(path)
                if stat:
                    return stat.st_mode
                return None
            
            def _mkdir(self, path):
                self.mkdir_in_existing_parent_exists_ok(path)

            def read_file_ex(self, source_path, target_fp, callback, interrupt_event):
                # Basic implementation ignoring callback progress for now
                try:
                    data = self.read_file(source_path)
                    target_fp.write(data)
                    if callback:
                        callback(len(data), len(data))
                except Exception as e:
                    # Map errors
                    raise ManagementError("Read error", "read", str(e), "") from e

            def write_file_ex(self, target_path, source_fp, file_size, callback):
                # Basic implementation ignoring callback progress for now
                try:
                    data = source_fp.read()
                    self.write_file_in_existing_dir(target_path, data)
                    if callback:
                        callback(len(data), len(data))
                except Exception as e:
                    raise ManagementError("Write error", "write", str(e), "") from e

        MINNY_AVAILABLE = True
    except ImportError:
        BareMetalTargetManager = None
        MicroPythonConnection = None
        ManagementError = Exception
        MINNY_AVAILABLE = False

# make sure thonny folder is in sys.path (relevant in dev)
thonny_container = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if thonny_container not in sys.path:
    sys.path.append(thonny_container)

import thonny
from thonny.backend import UploadDownloadMixin, convert_newlines_if_has_shebang
from thonny.common import (
    ALL_EXPLAINED_STATUS_CODE,
    PROCESS_ACK,
    BackendEvent,
    EOFCommand,
    ToplevelResponse,
    execute_system_command,
    serialize_message,
)
from thonny.plugins.micropython.mp_back import MicroPythonBackend

RAW_PASTE_COMMAND = b"\x05A\x01"
RAW_PASTE_CONFIRMATION = b"R\x01"
RAW_PASTE_REFUSAL = b"R\x00"
RAW_PASTE_CONTINUE = b"\x01"


BAUDRATE = 115200
ENCODING = "utf-8"

# Commands

# Output tokens
ESC = b"\x1b"
ST = b"\x1b\\"
VALUE_REPR_START = b"<repr>"
VALUE_REPR_END = b"</repr>"
NORMAL_PROMPT = b">>> "
LF = b"\n"
OK = b"OK"

# first prompt when switching to raw mode (or after soft reboot in raw mode)
# Looks like it's not translatable in CP
# https://github.com/adafruit/circuitpython/blob/master/locale/circuitpython.pot
FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\n>"

# https://forum.micropython.org/viewtopic.php?f=12&t=7652&hilit=w600#p43640
W600_FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\r\n>"

RAW_PROMPT = b">"

WEBREPL_REQ_S = "<2sBBQLH64s"
WEBREPL_PUT_FILE = 1
WEBREPL_GET_FILE = 2

TRACEBACK_MARKER = b"Traceback (most recent call last):"


# Can't use __name__, because it will be "__main__"
logger = getLogger("thonny.plugins.micropython.bare_metal_backend")


class BareMetalMicroPythonBackend(MicroPythonBackend, UploadDownloadMixin):
    def __init__(self, connection: MicroPythonConnection, clean: bool, args: Dict[str, Any]):

        tmgr = BareMetalTargetManager(
            connection,
            submit_mode=args.get("submit_mode") or "raw_paste",
            write_block_size=args.get("write_block_size") or 127,
            write_block_delay=args.get("write_block_delay") or 0.01,
            uses_local_time=args.get("local_rtc") or True,
            clean=clean,
            interrupt=args.get("interrupt_on_connect", False) or clean,
            cwd=args.get("cwd"),
        )
        super().__init__(tmgr)

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        logger.info("_run_main_program")
        assert isinstance(self._tmgr, BareMetalTargetManager)
        self._tmgr.launch_main_program()
        self._tmgr._process_output_until_active_prompt(self._send_output)
        self.send_message(ToplevelResponse(cwd=self._tmgr.get_cwd()))
        logger.debug("completed _run_main_program")

    def _cmd_execute_system_command(self, cmd) -> Dict[str, Any]:
        # Can't use stdin, because a thread is draining it
        returncode = execute_system_command(cmd, cwd=self._local_cwd, disconnect_stdin=True)
        return {"returncode": returncode}

    def _cmd_get_fs_info(self, cmd) -> Dict[str, Any]:
        if self._tmgr._using_simplified_micropython():
            used = self._evaluate(
                dedent(
                    """
                    __minny_helper.print_mgmt_value(
                        __minny_helper.builtins.sum([__minny_helper.os.size(name) for name in __minny_helper.os.listdir()])
                    )  
                    """
                )
            )
            return {
                "total": None,
                "used": used,
                "free": None,
                "comment": "Assuming around 30 kB of storage space for user files.",
            }

        else:
            result = self._evaluate(
                dedent(
                    """
                __thonny_stat = __minny_helper.os.statvfs(%r)
                __thonny_total = __thonny_stat[2] * __thonny_stat[0]
                __thonny_free = __thonny_stat[3] * __thonny_stat[0]

                __minny_helper.print_mgmt_value({
                    "total" : __thonny_total,
                    "used" : __thonny_total - __thonny_free,
                    "free": __thonny_free,
                })  

                del __thonny_stat 
                del __thonny_total
                del __thonny_free
                """
                )
                % cmd.path
            )

            return result

    def _cmd_upload(self, cmd):
        return super(BareMetalMicroPythonBackend, self)._cmd_upload(cmd)

    def _cmd_write_file(self, cmd):
        return super(BareMetalMicroPythonBackend, self)._cmd_write_file(cmd)

    def _cmd_prepare_disconnect(self, cmd):
        # NB! Don't let the mainloop see the prompt and act on it
        self._tmgr._prepare_disconnect()

    def _get_stat_mode_for_upload(self, path: str) -> Optional[int]:
        return self._tmgr._get_stat_mode(path)

    def _mkdir_for_upload(self, path: str) -> None:
        self._tmgr._mkdir(path)

    def _read_file(
        self, source_path: str, target_fp: BinaryIO, callback: Callable[[int, int], None]
    ) -> None:
        assert self._current_command_interrupt_event is not None
        start_time = time.time()
        self._tmgr.read_file_ex(
            source_path, target_fp, callback, self._current_command_interrupt_event
        )
        logger.info("Read %s in %.1f seconds", source_path, time.time() - start_time)

    def _write_file(
        self,
        source_fp: BinaryIO,
        target_path: str,
        file_size: int,
        callback: Callable[[int, int], None],
        make_shebang_scripts_executable: bool,
    ) -> None:
        start_time = time.time()

        if make_shebang_scripts_executable:
            source_fp, _ = convert_newlines_if_has_shebang(source_fp)
            # No need (or not possible?) to set mode on bare metal

        self._tmgr.write_file_ex(target_path, source_fp, file_size, callback)

        logger.info("Wrote %s in %.1f seconds", target_path, time.time() - start_time)

    def _report_internal_exception(self, msg: str) -> None:
        super()._report_internal_exception(msg)

        e = sys.exc_info()[1]
        if isinstance(e, ManagementError):
            self._log_management_error_details(e)

        self._show_error(
            'You may need to press "Stop/Restart" or hard-reset your '
            + "%s device and try again.\n" % self._tmgr._get_interpreter_kind()
        )


class GenericBareMetalMicroPythonBackend(BareMetalMicroPythonBackend):
    pass


def launch_bare_metal_backend(backend_class: Callable[..., BareMetalMicroPythonBackend]) -> None:
    thonny.configure_backend_logging()
    print(PROCESS_ACK)

    import ast

    args = ast.literal_eval(sys.argv[1])
    logger.info("Starting backend, args: %r", args)

    try:
        if args["port"] is None:
            print("\nPort not defined", file=sys.stderr)
            sys.exit(ALL_EXPLAINED_STATUS_CODE)
        elif args["port"] == "webrepl":
            try:
                from minny.webrepl_connection import WebReplConnection
            except ImportError:
                print("\nminny package not available. Cannot use WebREPL connection.", file=sys.stderr)
                sys.exit(ALL_EXPLAINED_STATUS_CODE)

            connection = WebReplConnection(args["url"], args["password"])
        else:
            try:
                from minny.serial_connection import SerialConnection
            except ImportError:
                print("\nminny package not available. Cannot use Serial connection.", file=sys.stderr)
                sys.exit(ALL_EXPLAINED_STATUS_CODE)

            connection = SerialConnection(
                args["port"], BAUDRATE, dtr=args.get("dtr"), rts=args.get("rts")
            )
            # connection = DifficultSerialConnection(args["port"], BAUDRATE)

        backend_class(connection, clean=args["clean"], args=args)

    except ConnectionError as e:
        text = "\n" + str(e) + "\n"
        msg = BackendEvent(event_type="ProgramOutput", stream_name="stderr", data=text)
        sys.stdout.write(serialize_message(msg) + "\n")
        sys.stdout.flush()
        sys.exit(ALL_EXPLAINED_STATUS_CODE)


if __name__ == "__main__":
    launch_bare_metal_backend(GenericBareMetalMicroPythonBackend)
