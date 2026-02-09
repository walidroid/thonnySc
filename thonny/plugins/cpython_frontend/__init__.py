from thonny import get_workbench
from thonny.languages import tr
from thonny.plugins.cpython_frontend.cp_front import (
    LocalCPythonConfigurationPage,
    LocalCPythonProxy,
    get_default_cpython_executable_for_backend,
)


def load_plugin():
    wb = get_workbench()
    wb.set_default("run.backend_name", "LocalCPython")
    wb.set_default("LocalCPython.last_executables", [])
    wb.set_default("LocalCPython.executable", get_default_cpython_executable_for_backend())

    if wb.get_option("run.backend_name") in ["PrivateVenv", "SameAsFrontend", "CustomCPython"]:
        # Removed in Thonny 4.0
        wb.set_option("run.backend_name", "LocalCPython")
        wb.set_option("LocalCPython.executable", get_default_cpython_executable_for_backend())
    
    # Force LocalCPython (Python 3) as the default backend on startup
    # Override any saved backend preference (e.g., ESP32) to ensure
    # Thonny always starts with Python 3 interpreter
    if wb.get_option("run.backend_name") != "LocalCPython":
        wb.set_option("run.backend_name", "LocalCPython")

    wb.add_backend(
        "LocalCPython",
        LocalCPythonProxy,
        tr("Local Python 3"),
        LocalCPythonConfigurationPage,
        "02",
    )
