@echo off
echo Starting Thonny 4.1.7 from source...

REM Kill zombie Thonny processes from previous runs
taskkill /F /IM Thonny.exe /T >nul 2>&1

REM Clean stale IPC files to prevent delegation conflicts
del /Q "%LOCALAPPDATA%\thonny-*\ipc.sock" >nul 2>&1

REM Try bundled python first IF it has tkinter
if exist "Python\python.exe" (
    ".\Python\python.exe" -c "import tkinter" >nul 2>&1
    if not errorlevel 1 (
         echo Using bundled Python...
         ".\Python\python.exe" launch_thonny.py
         goto :EOF
    ) else (
         echo Bundled Python found but lacks tkinter - skipping...
    )
)

REM Try system python
py -3 -c "import tkinter" >nul 2>&1
if not errorlevel 1 (
     echo Using system Python...
     py -3 launch_thonny.py
     goto :EOF
)

echo.
echo CRITICAL: Valid Python 3 with tkinter not found!
echo.
echo Please install Python 3.13 from python.org:
echo 1. Download Windows installer (64-bit)
echo 2. Check "Add Python to PATH"
echo 3. Check "tcl/tk and IDLE" (usually checked by default)
echo.
echo After installing, run: pip install -r requirements.txt
echo.
pause
