"""
PyQt5 exception handling utilities.

The handler keeps full tracebacks in a log file while presenting only the last
three meaningful lines to the user. It also suppresses repeated summaries so a
burst of identical errors does not flood the console or dialogs.
"""

from __future__ import annotations

import functools
import logging
import os
import sys
import threading
import time
import traceback
from types import TracebackType
from typing import Any, Callable, Optional, Tuple, Type, TypeVar

import thonny

T = TypeVar("T")
ExceptionInfo = Tuple[Type[BaseException], BaseException, Optional[TracebackType]]

_DEFAULT_LOG_FILE = os.path.join(thonny.THONNY_USER_DIR, "pyqt5_errors.log")
_DEFAULT_MAX_SUMMARY_LINES = 3
_DEFAULT_REPEAT_WINDOW_SECONDS = 1.5
_LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d [%(threadName)s] %(levelname)-7s %(name)s: %(message)s"
)
_FRAME_SKIP_TOKENS = (
    os.path.normcase("PyQt5"),
    os.path.normcase("importlib"),
    os.path.normcase("threading.py"),
    os.path.normcase("runpy.py"),
    os.path.normcase("pyqt5_error_handler.py"),
)

_STATE: Optional["_ExceptionHandlerState"] = None


def _safe_import_pyqt5():
    try:
        from PyQt5 import QtCore, QtWidgets

        return QtCore, QtWidgets
    except ImportError:
        return None, None


def _configure_file_logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger("thonny.pyqt5_errors")
    logger.setLevel(logging.ERROR)
    logger.propagate = False

    target = os.path.abspath(log_file)
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler) and os.path.abspath(handler.baseFilename) == target:
            return logger

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    os.makedirs(os.path.dirname(target), exist_ok=True)
    file_handler = logging.FileHandler(target, encoding="utf-8", mode="a")
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, "%H:%M:%S"))
    logger.addHandler(file_handler)
    return logger


def _is_meaningful_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped == "Traceback (most recent call last):":
        return False
    if set(stripped) <= {"^", "~"}:
        return False
    return True


def _pick_relevant_frame(exc_tb: Optional[TracebackType]):
    if exc_tb is None:
        return None

    frames = traceback.extract_tb(exc_tb)
    if not frames:
        return None

    for frame in reversed(frames):
        normalized = os.path.normcase(frame.filename)
        if any(token in normalized for token in _FRAME_SKIP_TOKENS):
            continue
        return frame

    return frames[-1]


def _format_exception_only_line(exc_type: Type[BaseException], exc_value: BaseException) -> str:
    message = str(exc_value).strip()
    if message:
        return f"{exc_type.__name__}: {message}"
    return exc_type.__name__


def _build_summary_lines(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_tb: Optional[TracebackType],
    max_lines: int,
) -> list[str]:
    lines: list[str] = []

    if isinstance(exc_value, SyntaxError):
        filename = exc_value.filename or "<unknown>"
        lineno = exc_value.lineno or 0
        lines.append(f'File "{filename}", line {lineno}')

        bad_line = (exc_value.text or "").rstrip()
        if _is_meaningful_line(bad_line):
            lines.append(bad_line.strip())

        lines.append(_format_exception_only_line(exc_type, exc_value))
        return lines[-max_lines:]

    frame = _pick_relevant_frame(exc_tb)
    if frame is not None:
        location = f'File "{frame.filename}", line {frame.lineno}'
        if frame.name:
            location += f", in {frame.name}"
        lines.append(location)

        if _is_meaningful_line(frame.line or ""):
            lines.append((frame.line or "").strip())

    lines.append(_format_exception_only_line(exc_type, exc_value))
    lines = [line for line in lines if _is_meaningful_line(line)]
    return lines[-max_lines:]


class _DialogBridge:
    def __init__(self, state: "_ExceptionHandlerState", app: Any, qt_core: Any, qt_widgets: Any) -> None:
        self._state = state
        self._qt_widgets = qt_widgets

        class Bridge(qt_core.QObject):
            show_summary = qt_core.pyqtSignal(object)

        self._bridge = Bridge()
        self._bridge.moveToThread(app.thread())
        self._bridge.show_summary.connect(self._show_dialog, qt_core.Qt.QueuedConnection)

    def emit(self, summary_lines: list[str]) -> None:
        self._bridge.show_summary.emit(summary_lines)

    def _show_dialog(self, summary_lines: list[str]) -> None:
        if not summary_lines:
            return

        box = self._qt_widgets.QMessageBox(self._qt_widgets.QApplication.activeWindow())
        box.setIcon(self._qt_widgets.QMessageBox.Critical)
        box.setWindowTitle("PyQt5 Error")
        box.setText(summary_lines[0])
        box.setInformativeText("\n".join(summary_lines[1:]))
        box.setDetailedText(f"Full traceback logged to:\n{self._state.log_file}")
        box.exec_()


class _ExceptionHandlerState:
    def __init__(
        self,
        log_file: str,
        max_summary_lines: int,
        show_dialogs: bool,
        repeat_window_seconds: float,
    ) -> None:
        self.log_file = os.path.abspath(log_file)
        self.max_summary_lines = max(1, max_summary_lines)
        self.show_dialogs = show_dialogs
        self.repeat_window_seconds = max(0.0, repeat_window_seconds)
        self.logger = _configure_file_logger(self.log_file)
        self.original_sys_excepthook = sys.excepthook
        self.original_threading_excepthook = getattr(threading, "excepthook", None)
        self.original_qapplication_init = None
        self.original_qapplication_notify = None
        self.original_qt_message_handler = None
        self.dialog_bridge: Optional[_DialogBridge] = None
        self.last_signature: Optional[Tuple[str, ...]] = None
        self.last_timestamp = 0.0
        self.repeat_count = 0

    def install(self, app: Any = None) -> None:
        sys.excepthook = self.handle_sys_exception

        if self.original_threading_excepthook is not None:
            threading.excepthook = self.handle_thread_exception

        qt_core, qt_widgets = _safe_import_pyqt5()
        if qt_core is None or qt_widgets is None:
            return

        if self.original_qapplication_notify is None:
            self.original_qapplication_notify = qt_widgets.QApplication.notify

            @functools.wraps(self.original_qapplication_notify)
            def safe_notify(qapp, receiver, event):
                try:
                    return self.original_qapplication_notify(qapp, receiver, event)
                except Exception:
                    self.report_current_exception("Qt event handler")
                    return False

            qt_widgets.QApplication.notify = safe_notify

        if self.original_qapplication_init is None:
            self.original_qapplication_init = qt_widgets.QApplication.__init__

            @functools.wraps(self.original_qapplication_init)
            def safe_qapplication_init(qapp, *args, **kwargs):
                self.original_qapplication_init(qapp, *args, **kwargs)
                self._ensure_dialog_bridge(qapp, qt_core, qt_widgets)

            qt_widgets.QApplication.__init__ = safe_qapplication_init

        if self.original_qt_message_handler is None:
            self.original_qt_message_handler = qt_core.qInstallMessageHandler(self.handle_qt_message)

        if app is None:
            app = qt_widgets.QApplication.instance()

        self._ensure_dialog_bridge(app, qt_core, qt_widgets)

    def handle_sys_exception(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.handle_exception(exc_type, exc_value, exc_tb, source="sys.excepthook")

    def handle_thread_exception(self, args) -> None:
        source = "worker thread"
        thread_name = getattr(getattr(args, "thread", None), "name", "")
        if thread_name:
            source = f"worker thread {thread_name}"

        self.handle_exception(
            args.exc_type,
            args.exc_value,
            args.exc_traceback,
            source=source,
        )

    def handle_qt_message(self, mode, context, message) -> None:
        mode_name = getattr(mode, "name", str(mode))
        where = ""
        if context is not None and getattr(context, "file", None):
            where = f" ({context.file}:{getattr(context, 'line', 0)})"

        self.logger.error("Qt message [%s]%s: %s", mode_name, where, message)

    def report_current_exception(self, source: str) -> None:
        exc_info = sys.exc_info()
        exc_type, exc_value, exc_tb = exc_info
        if exc_type is None or exc_value is None:
            return

        self.handle_exception(exc_type, exc_value, exc_tb, source=source)

    def handle_exception(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        exc_tb: Optional[TracebackType],
        source: str,
    ) -> None:
        if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
            self.original_sys_excepthook(exc_type, exc_value, exc_tb)
            return

        summary_lines = _build_summary_lines(
            exc_type,
            exc_value,
            exc_tb,
            self.max_summary_lines,
        )
        if not summary_lines:
            summary_lines = [_format_exception_only_line(exc_type, exc_value)]

        self.logger.error("Unhandled PyQt5 exception from %s", source, exc_info=(exc_type, exc_value, exc_tb))

        if self._is_repeated(summary_lines):
            return

        print("\n".join(summary_lines), file=sys.stderr)

        if self.show_dialogs and self.dialog_bridge is not None:
            self.dialog_bridge.emit(summary_lines)

    def _is_repeated(self, summary_lines: list[str]) -> bool:
        signature = tuple(summary_lines)
        now = time.monotonic()
        repeated = (
            signature == self.last_signature
            and now - self.last_timestamp <= self.repeat_window_seconds
        )

        self.last_signature = signature
        self.last_timestamp = now
        if repeated:
            self.repeat_count += 1
        else:
            self.repeat_count = 1

        return repeated

    def _ensure_dialog_bridge(self, app: Any, qt_core: Any, qt_widgets: Any) -> None:
        if not self.show_dialogs or app is None or self.dialog_bridge is not None:
            return

        self.dialog_bridge = _DialogBridge(self, app, qt_core, qt_widgets)


def install_pyqt5_exception_handling(
    app: Any = None,
    *,
    log_file: str = _DEFAULT_LOG_FILE,
    max_summary_lines: int = _DEFAULT_MAX_SUMMARY_LINES,
    show_dialogs: bool = True,
    repeat_window_seconds: float = _DEFAULT_REPEAT_WINDOW_SECONDS,
) -> _ExceptionHandlerState:
    global _STATE

    if _STATE is None:
        _STATE = _ExceptionHandlerState(
            log_file=log_file,
            max_summary_lines=max_summary_lines,
            show_dialogs=show_dialogs,
            repeat_window_seconds=repeat_window_seconds,
        )
    else:
        _STATE.show_dialogs = show_dialogs

    _STATE.install(app)
    return _STATE


def handle_current_exception(source: str = "PyQt callback") -> None:
    install_pyqt5_exception_handling().report_current_exception(source)


def guard_callable(
    func: Optional[Callable[..., T]] = None,
    *,
    source: Optional[str] = None,
    reraise: bool = False,
):
    def decorator(callback: Callable[..., T]) -> Callable[..., Optional[T]]:
        label = source or callback.__name__

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            try:
                return callback(*args, **kwargs)
            except Exception:
                handle_current_exception(label)
                if reraise:
                    raise
                return None

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


def guard_slot(*slot_args, **slot_kwargs):
    qt_core, _qt_widgets = _safe_import_pyqt5()

    def decorator(callback: Callable[..., T]):
        wrapped = guard_callable(callback, source=f"slot {callback.__name__}")
        if qt_core is None:
            return wrapped

        return qt_core.pyqtSlot(*slot_args, **slot_kwargs)(wrapped)

    return decorator


def load_plugin() -> None:
    install_pyqt5_exception_handling()
