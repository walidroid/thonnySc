import sys
import os
import traceback

with open("diag_serial_result.txt", "w") as f:
    f.write(f"Python: {sys.version}\n")
    f.write(f"Executable: {sys.executable}\n")
    f.write(f"sys.path: {sys.path}\n\n")

    try:
        import serial
        f.write(f"OK: import serial\n")
        f.write(f"File: {serial.__file__}\n")
    except ImportError as e:
        f.write(f"FAIL: import serial\n")
        f.write(f"Error: {e}\n")
        f.write(traceback.format_exc() + "\n")

    try:
        from serial.tools.list_ports import comports
        f.write(f"OK: from serial.tools.list_ports import comports\n")
    except ImportError as e:
        f.write(f"FAIL: import comports\n")
        f.write(f"Error: {e}\n")
        f.write(traceback.format_exc() + "\n")
