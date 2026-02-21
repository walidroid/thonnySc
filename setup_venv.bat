@echo off
echo ==============================================
echo Setup Virtual Environment for ThonnySc
echo ==============================================

if not exist venv (
    echo Creating Python 3.13 Virtual Environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        echo Make sure Python 3.13 is installed and in your PATH.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment 'venv' already exists.
)

echo.
echo Activating Virtual Environment...
call venv\Scripts\activate.bat

echo.
echo Installing Requirements...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ==============================================
echo Setup Complete!
echo You can now use run_thonny.bat to launch ThonnySc.
echo ==============================================
pause
