param (
    [string]$Version = "1.0.0"
)

# ThonnySc Build Script
# This script downloads Python embeddable package and builds the installer locally

Write-Host "=== ThonnySc Build Script ===" -ForegroundColor Green
Write-Host "Building version: $Version" -ForegroundColor Green
Set-Location -Path $PSScriptRoot

# Step 1: Verify System Python (Using Host Environment)
Write-Host "`n[1/5] Verifying System Python Environment..." -ForegroundColor Cyan

$pyVersionReq = "3.13"
$pyCmd = $null

if (Get-Command "py" -ErrorAction SilentlyContinue) {
    try {
        $testVer = py -3.13 --version 2>&1
        if ($testVer -match "3.13") {
            $pyCmd = "py -3.13"
            Write-Host "Found Python Launcher: $testVer" -ForegroundColor Green
        }
    } catch {}
}

if (-not $pyCmd -and (Get-Command "python" -ErrorAction SilentlyContinue)) {
    $testVer = python --version 2>&1
    if ($testVer -match "3.13") {
        $pyCmd = "python"
        Write-Host "Found Python Command: $testVer" -ForegroundColor Green
    }
}

if (-not $pyCmd) {
    Write-Host "ERROR: robust Python 3.13 installation not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.13 from python.org and add to PATH."
    exit 1
}

# Step 2: Prepare Build Environment
Write-Host "`n[2/5] Preparing Build Environment..." -ForegroundColor Cyan
if (Test-Path "Python") { Remove-Item "Python" -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path "_internal") { Remove-Item "_internal" -Recurse -Force -ErrorAction SilentlyContinue }

# Verify standard libraries are loadable
& $pyCmd -c "import tkinter; import _tkinter; print('Tkinter OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: System Python does not appear to have Tkinter installed properly." -ForegroundColor Yellow
}

# Step 2.5: Verify Qt Designer (Standalone)
Write-Host "`n[2.5/5] Verify Qt Designer..." -ForegroundColor Cyan
$qtDesignerPath = "Qt Designer\designer.exe"
if (-not (Test-Path $qtDesignerPath)) {
     Write-Host "Qt Designer not found locally. Attempting download..." -ForegroundColor Yellow
     # (Keep existing download logic or rely on artifact)
     try {
        $downloadUrl = "https://github.com/walidroid/thonnySc/releases/download/qt-designer/qt-designer.zip"
        Invoke-WebRequest $downloadUrl -Out "qt-designer.zip"
        Expand-Archive "qt-designer.zip" -DestinationPath "Qt Designer" -Force
        Remove-Item "qt-designer.zip" -Force
     } catch {
        Write-Host "Failed to download Qt Designer: $_" -ForegroundColor Red
     }
}

# Step 2.6: Install Language Server Dependencies
Write-Host "`n[2.6/5] Installing Language Server Dependencies..." -ForegroundColor Cyan

Write-Host "Installing ruff for code linting..."
& $pyCmd -m pip install ruff --no-warn-script-location

if ($LASTEXITCODE -eq 0) {
    Write-Host "Ruff installed successfully" -ForegroundColor Green
    
    # Verify installation
    $ruffCheck = & $pyCmd -c "import ruff; print('OK')" 2>$null
    if ($ruffCheck -eq "OK") {
        Write-Host "Ruff verification successful" -ForegroundColor Green
    } else {
        Write-Host "Warning: Ruff verification failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: Ruff installation failed - language server features may not work" -ForegroundColor Yellow
}

# Step 2.6.1: Install PyQt5 for Qt Designer
Write-Host "`nInstalling PyQt5 for .ui file loading..."
& $pyCmd -m pip install PyQt5 --no-warn-script-location

if ($LASTEXITCODE -eq 0) {
    Write-Host "PyQt5 installed successfully" -ForegroundColor Green
    
    # Verify installation
    $pyqt5Check = & $pyCmd -c "from PyQt5.uic import loadUi; print('OK')" 2>$null
    if ($pyqt5Check -eq "OK") {
        Write-Host "PyQt5.uic verification successful" -ForegroundColor Green
    } else {
        Write-Host "Warning: PyQt5.uic verification failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: PyQt5 installation failed - .ui files may not load" -ForegroundColor Yellow
}

# Step 2.6.2: Install esptool for ESP32/ESP8266
Write-Host "`nInstalling esptool for ESP32/ESP8266 support..."
& $pyCmd -m pip install esptool>=4.0 --no-warn-script-location

if ($LASTEXITCODE -eq 0) {
    Write-Host "esptool installed successfully" -ForegroundColor Green
    
    # Verify installation
    $esptoolCheck = & $pyCmd -c "import esptool; print('OK')" 2>$null
    if ($esptoolCheck -eq "OK") {
        Write-Host "esptool verification successful" -ForegroundColor Green
    } else {
        Write-Host "Warning: esptool verification failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: esptool installation failed - ESP32/ESP8266 support unavailable" -ForegroundColor Yellow
}

# Step 2.6.3: Install minny for backend communication (Optional/Local)
# Write-Host "`nInstalling minny for backend communication..."
# & $pyCmd -m pip install minny --no-warn-script-location

# Step 2.6.5: Install jedi for code completion
Write-Host "`nInstalling jedi for code completion..."
& $pyCmd -m pip install "jedi>=0.19.0" --no-warn-script-location

if ($LASTEXITCODE -eq 0) {
    Write-Host "jedi installed successfully" -ForegroundColor Green
    
    # Verify installation
    $jediCheck = & $pyCmd -c "import jedi; print('OK')" 2>$null
    if ($jediCheck -eq "OK") {
        Write-Host "jedi verification successful" -ForegroundColor Green
    } else {
        Write-Host "Warning: jedi verification failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: jedi installation failed - Code completion may not work" -ForegroundColor Yellow
}

# Step 2.6.6: Install serial port packages
Write-Host "`nInstalling pyserial and adafruit-board-toolkit for serial port detection..."
& $pyCmd -m pip install pyserial>=3.5 "adafruit-board-toolkit>=1.1.0" --no-warn-script-location

if ($LASTEXITCODE -eq 0) {
    Write-Host "Serial port packages installed successfully" -ForegroundColor Green
    
    # Verify installation
    $serialCheck = & $pyCmd -c "import serial; import adafruit_board_toolkit; print('OK')" 2>$null
    if ($serialCheck -eq "OK") {
        Write-Host "Serial port packages verification successful" -ForegroundColor Green
    } else {
        Write-Host "Warning: Serial port packages verification failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: Serial port packages installation failed - ESP32/MicroPython serial detection may not work" -ForegroundColor Yellow
}

# Step 2.6.4: Install thonny-autosave and missing stdlib dependencies
Write-Host "`nInstalling thonny-autosave..."
# Install the plugin (no-deps to avoid installing older Thonny version)
& $pyCmd -m pip install thonny-autosave --no-deps --no-warn-script-location

$numpyTarget = "numpy"
Write-Host "`nInstalling $numpyTarget..." -ForegroundColor Cyan
& $pyCmd -m pip install $numpyTarget --no-warn-script-location
if ($LASTEXITCODE -eq 0) {
    $numpyCheck = & $pyCmd -c "import numpy as np; import numpy.linalg; print('OK')" 2>$null
    if ($numpyCheck -eq "OK") {
        Write-Host "numpy verification successful" -ForegroundColor Green
    } else {
        Write-Host "Warning: numpy verification failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: numpy installation failed" -ForegroundColor Yellow
}

$requirementsPath = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $requirementsPath) {
    Write-Host "`nInstalling requirements.txt..." -ForegroundColor Cyan
    & ".\Python\python.exe" -m pip install -r $requirementsPath --no-warn-script-location --no-cache-dir --no-binary mypy
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Requirements installation failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "WARNING: requirements.txt not found at $requirementsPath" -ForegroundColor Yellow
}

# Step 2.7: Clean up problematic plugins
Write-Host "`n[2.7/5] Cleaning up incompatible plugins..." -ForegroundColor Cyan

# Remove thonny_friendly (incompatible API)
if (Test-Path "thonnycontrib\thonny_friendly") {
    Remove-Item "thonnycontrib\thonny_friendly" -Recurse -Force
    Write-Host "Removed incompatible thonny_friendly plugin" -ForegroundColor Green
}

# thonny-autosave restored (sched.py provided)

# Step 2.8: Remove unused locale directories
Write-Host "`n[2.8/5] Removing unused locale directories..." -ForegroundColor Cyan
$localeDir = "thonny\locale"
if (Test-Path $localeDir) {
    $keepDirs = @("fr_FR", "en_US")
    Get-ChildItem $localeDir -Directory | Where-Object { $_.Name -notin $keepDirs } | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force
        Write-Host "  Removed locale: $($_.Name)"
    }
    Write-Host "Locale cleanup complete" -ForegroundColor Green
}

# Step 3: Build with PyInstaller
Write-Host "`n[3/5] Building with PyInstaller..." -ForegroundColor Cyan

# Install dependencies into System Python for PyInstaller visibility
Write-Host "Installing dependencies/requirements from requirements.txt..."
if (Test-Path "requirements.txt") {
    & $pyCmd -m pip install -r requirements.txt --no-warn-script-location
} else {
    Write-Host "requirements.txt not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Installing PyInstaller..."
& $pyCmd -m pip install pyinstaller --no-warn-script-location

Write-Host "Running PyInstaller..."
& $pyCmd -m PyInstaller thonny.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "PyInstaller build completed" -ForegroundColor Green

# Post-Build: Copy local plugins to ensure they are present
Write-Host "Copying local plugins to dist/Thonny..."
if (Test-Path "local_plugins\thonnycontrib") {
    $dest = "dist\Thonny\thonnycontrib"
    if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }
    Copy-Item "local_plugins\thonnycontrib\*" -Destination $dest -Recurse -Force
    Write-Host "Copied local plugins to $dest" -ForegroundColor Green
} else {
    Write-Host "Warning: local_plugins\thonnycontrib not found" -ForegroundColor Yellow
}

# Post-Build: Copy launch_thonny.py to dist (for Tcl/Tk auto-detection)
if (Test-Path "launch_thonny.py") {
    Copy-Item "launch_thonny.py" -Destination "dist\Thonny\launch_thonny.py" -Force
    Write-Host "Copied launch_thonny.py to dist" -ForegroundColor Green
}

# Step 4: Build Installer
Write-Host "`n[4/5] Building Installer with Inno Setup..." -ForegroundColor Cyan
# Version is passed as parameter
$innoPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (Test-Path $innoPath) {
    & $innoPath /DMyAppVersion=$Version installer.iss
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installer created successfully!" -ForegroundColor Green
    } else {
        Write-Host "Installer compilation failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Inno Setup not found at: $innoPath" -ForegroundColor Red
    Write-Host "Please install Inno Setup 6 from https://jrsoftware.org/isinfo.php" -ForegroundColor Yellow
    exit 1
}

# Step 5: Summary
Write-Host "`n[5/5] Build Complete!" -ForegroundColor Green
Write-Host "`nOutput:" -ForegroundColor Cyan
if (Test-Path "output\ThonnySc_v$Version.exe") {
    $size = (Get-Item "output\ThonnySc_v$Version.exe").Length / 1MB
    Write-Host "  Installer: output\ThonnySc_v$Version.exe ($([math]::Round($size, 2)) MB)" -ForegroundColor White
}

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Test the installer: .\output\ThonnySc_v$Version.exe"
Write-Host "  2. Verify backend starts correctly"
Write-Host "  3. Try opening and running Python files"
