@echo off
title Mise a jour de ThonnySc
:: Demande automatique des privileges administrateur si necessaire
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Demande des droits administrateur pour mettre a jour ThonnySc...
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0""", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /b
)

cd /d "%~dp0"

echo ========================================================
echo Mise a jour des fichiers ThonnySc dans Program Files...
echo ========================================================

set "INSTALL_DIR=C:\Program Files (x86)\ThonnySc"

if not exist "%INSTALL_DIR%" (
    echo [ERREUR] Dossier introuvable : %INSTALL_DIR%
    pause
    exit /b 1
)

echo 1. Copie des correctifs MicroPython / ESP32...
copy /y "thonny\plugins\micropython\base_flashing_dialog.py" "%INSTALL_DIR%\_internal\thonny\plugins\micropython\base_flashing_dialog.py"
copy /y "thonny\plugins\micropython\esptool_dialog.py" "%INSTALL_DIR%\_internal\thonny\plugins\micropython\esptool_dialog.py"
copy /y "thonny\plugins\micropython\__init__.py" "%INSTALL_DIR%\_internal\thonny\plugins\micropython\__init__.py"

echo 2. Copie du menu Interpreteur (thonny_quick_switch)...
if exist "%INSTALL_DIR%\thonnycontrib\thonny_quick_switch" (
    copy /y "local_plugins\thonnycontrib\thonny_quick_switch\*" "%INSTALL_DIR%\thonnycontrib\thonny_quick_switch\"
)
if exist "%INSTALL_DIR%\_internal\thonnycontrib\thonny_quick_switch" (
    copy /y "local_plugins\thonnycontrib\thonny_quick_switch\*" "%INSTALL_DIR%\_internal\thonnycontrib\thonny_quick_switch\"
)

echo 3. Copie de l'autocompletion corrigee (thonny_simple_autocomplete)...
if exist "%INSTALL_DIR%\thonnycontrib\thonny_simple_autocomplete" (
    copy /y "local_plugins\thonnycontrib\thonny_simple_autocomplete\*" "%INSTALL_DIR%\thonnycontrib\thonny_simple_autocomplete\"
)
if exist "%INSTALL_DIR%\_internal\thonnycontrib\thonny_simple_autocomplete" (
    copy /y "local_plugins\thonnycontrib\thonny_simple_autocomplete\*" "%INSTALL_DIR%\_internal\thonnycontrib\thonny_simple_autocomplete\"
)

echo.
echo ========================================================
echo Mise a jour effectuee avec succes !
echo Vous pouvez maintenant relancer ThonnySc.
echo ========================================================
echo.
pause
