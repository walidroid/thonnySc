@echo off
echo Starting Thonny 4.1.7 from source...

REM Kill zombie Thonny processes from previous runs
taskkill /F /IM Thonny.exe /T >nul 2>&1

REM Clean stale IPC files to prevent delegation conflicts
del /Q "%LOCALAPPDATA%\thonny-*\ipc.sock" >nul 2>&1

py -3 launch_thonny.py
pause
