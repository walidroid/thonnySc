@echo off
echo ==============================================
echo Launching ThonnySc in Virtual Environment
echo ==============================================

if not exist venv\Scripts\activate.bat (
    echo ERROR: Virtual environment not found!
    echo Please run setup_venv.bat first.
    pause
    exit /b 1
)

echo Activating environment...
call venv\Scripts\activate.bat

echo Starting Thonny...
python launch_thonny.py

if errorlevel 1 (
    echo.
    echo ----------------------------------------------
    echo ERROR: Thonny encountered a problem.
    echo ----------------------------------------------
    pause
)
