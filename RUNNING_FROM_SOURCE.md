# Running Thonny from Source

This document explains how to run the modified Thonny 4.1.7 from source code.

## Quick Start

### Windows
```cmd
RunThonny417.bat
```
or
```cmd
py -3 launch_thonny.py
```

### Linux/macOS
```bash
chmod +x run_thonny.sh
./run_thonny.sh
```
or
```bash
python3 launch_thonny.py
```

## Requirements

- **Python 3.11 or higher** with tkinter support
- Required packages (install via `pip install -r requirements.txt`):
  - esptool
  - pyserial
  - adafruit-board-toolkit

## Automated Setup

The `launch_thonny.py` script automatically:
- Detects and configures Tcl/Tk libraries for tkinter (Windows)
- Adds the project root to `sys.path`
- Provides detailed debug output for troubleshooting

## Key Modifications from Upstream

### Bug Fixes
1. **Single-instance mode**: Re-enabled (`SINGLE_INSTANCE_DEFAULT = True`)
2. **File loading**: Fixed to skip directories when loading startup files
3. **Working directory**: Configuration updated to use valid paths

### Customizations
- Custom toolbar with buttons: New, Open, Save, Run, Stop, Qt Designer, PyQt Code
- ESP32 backend integration
- Custom error translator plugin

## Configuration

User configuration is stored in:
- **Windows**: `C:\Users\<USERNAME>\AppData\Roaming\Thonny\configuration.ini`
- **Linux**: `~/.config/Thonny/configuration.ini`
- **macOS**: `~/Library/Thonny/configuration.ini`

### Important Settings
- `run.working_directory`: Should be a valid directory path (not `C:\`)
- `file.current_file`: Should be a valid file path or `None`

## Troubleshooting

### "Can't find a usable init.tcl"
The `launch_thonny.py` script auto-detects Tcl/Tk libraries. If it fails:
1. Ensure Python was installed with tkinter support
2. Manually set environment variables:
   ```cmd
   set TCL_LIBRARY=C:\path\to\python\tcl\tcl8.6
   set TK_LIBRARY=C:\path\to\python\tcl\tk8.6
   ```

### "INTERNAL ERROR, got '' instead of 'OK'"
This indicates backend communication failure. Check:
1. Working directory is valid in configuration
2. Python interpreter has required packages installed
3. No firewall blocking local IPC

### Multiple Instances Launching
Ensure `SINGLE_INSTANCE_DEFAULT = True` in `thonny/__init__.py`

## GitHub Actions Integration

The project includes automated build workflows:
- `.github/workflows/build.yml` - Main build workflow
- `.github/workflows/build-exe.yml` - Executable/installer build

The portable fixes are compatible with CI/CD environments as they auto-detect system configuration.

## Development

To modify the codebase:
1. Edit files in the `thonny/` directory
2. Test using `launch_thonny.py`
3. Commit changes to version control

No rebuild is required for Python source changes - they take effect immediately on next launch.
