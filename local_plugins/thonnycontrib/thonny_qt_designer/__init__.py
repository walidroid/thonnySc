"""
Qt Designer launcher plugin for ThonnySc.
Adds a 'Qt Designer' entry in the Tools menu and a toolbar button.
Qt Designer is launched from:
  1. The bundled 'Qt Designer/' folder next to Thonny.exe (installer)
  2. qt5_applications package (if installed in the embeddable Python)
  3. System-installed designer.exe on PATH
"""
import os
import subprocess
import sys
from logging import getLogger

logger = getLogger(__name__)


def _find_designer_exe() -> str | None:
    """Return the path to designer.exe, or None if not found."""
    candidates = []

    # 1. Bundled alongside the executable (installer layout)
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle: Thonny.exe sits in {app}\
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running from source: look relative to project root
        app_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )

    candidates.append(os.path.join(app_dir, "Qt Designer", "designer.exe"))

    # 2. qt5_applications package (installed via pip in bundled Python)
    try:
        import qt5_applications  # type: ignore[import]
        qt5_dir = os.path.dirname(qt5_applications.__file__)
        candidates.append(os.path.join(qt5_dir, "Qt", "bin", "designer.exe"))
    except ImportError:
        pass

    # Also check bundled Python's site-packages
    if getattr(sys, "frozen", False):
        python_dir = os.path.join(app_dir, "Python")
    else:
        python_dir = None

    if python_dir:
        candidates.append(
            os.path.join(
                python_dir, "Lib", "site-packages",
                "qt5_applications", "Qt", "bin", "designer.exe"
            )
        )

    # 3. System PATH
    import shutil
    found = shutil.which("designer")
    if found:
        candidates.append(found)

    for path in candidates:
        if os.path.isfile(path):
            logger.debug("Qt Designer found at: %s", path)
            return path

    return None


def _launch_designer():
    """Launch Qt Designer. Show an error message if not found."""
    from thonny import get_workbench

    exe = _find_designer_exe()
    if exe:
        try:
            subprocess.Popen([exe], cwd=os.path.dirname(exe))
        except Exception as e:
            logger.exception("Failed to launch Qt Designer")
            from tkinter import messagebox
            messagebox.showerror(
                "Qt Designer",
                f"Failed to launch Qt Designer:\n{e}",
                master=get_workbench(),
            )
    else:
        from tkinter import messagebox
        messagebox.showwarning(
            "Qt Designer Not Found",
            "Qt Designer was not found.\n\n"
            "It should be bundled in the 'Qt Designer\\' folder next to ThonnySc.exe.\n\n"
            "You can also install it via:\n"
            "  pip install qt5-applications",
            master=get_workbench(),
        )


def load_plugin():
    from thonny import get_workbench

    wb = get_workbench()

    # Register the toolbar button image
    # Frozen bundle: buttons/ is in _MEIPASS (same level as thonnycontrib/)
    # Source: buttons/ is at project root, 4 levels up from this file
    if getattr(sys, "frozen", False):
        buttons_dir = os.path.join(sys._MEIPASS, "buttons")
    else:
        buttons_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "buttons")
        )

    img_path = os.path.join(buttons_dir, "button_qt-designer.png")
    if os.path.isfile(img_path):
        try:
            wb.get_image(img_path, "qt-designer")
        except KeyError:
            # Theme mapping may not be initialized yet at plugin load time;
            # register the image after the workbench is fully set up.
            logger.debug("get_image called before theme was initialized; deferring image registration.")
            def deferred_registration():
                try:
                    wb.get_image(img_path, "qt-designer")
                except Exception:
                    logger.debug("Deferred get_image failed")

            wb.after(100, deferred_registration)

    # Add Tools > Qt Designer menu command
    wb.add_command(
        command_id="open_qt_designer",
        menu_name="tools",
        command_label="Qt Designer",
        handler=_launch_designer,
        image="qt-designer",
        include_in_toolbar=True,
        group=110,
    )
