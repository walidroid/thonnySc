param (
    [string]$Version = "1.0.0"
)

# ThonnySc Build Script
# This script builds the installer using System Python 3.13

Write-Host "=== ThonnySc Build Script ===" -ForegroundColor Green
Write-Host "Building version: $Version" -ForegroundColor Green
Set-Location -Path $PSScriptRoot

# Step 1: Verify System Python (Using Host Environment)
Write-Host "`n[1/5] Verifying System Python Environment..." -ForegroundColor Cyan

$pyVersionReq = "3.13"
$pyExe = $null
$pyBaseArgs = @()

if (Get-Command "py" -ErrorAction SilentlyContinue) {
    try {
        $testVer = py -3.13 --version 2>&1
        if ($testVer -match "3.13") {
            $pyExe = "py"
            $pyBaseArgs = @("-3.13")
            Write-Host "Found Python Launcher: $testVer" -ForegroundColor Green
        }
    } catch {}
}

if (-not $pyExe -and (Get-Command "python" -ErrorAction SilentlyContinue)) {
    $testVer = python --version 2>&1
    if ($testVer -match "3.13") {
        $pyExe = "python"
        $pyBaseArgs = @()
        Write-Host "Found Python Command: $testVer" -ForegroundColor Green
    }
}

if (-not $pyExe) {
    Write-Host "ERROR: robust Python 3.13 installation not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.13 from python.org and add to PATH."
    exit 1
}

# Step 2: Prepare Build Environment
Write-Host "`n[2/5] Preparing Build Environment..." -ForegroundColor Cyan
if (Test-Path "Python") { Remove-Item "Python" -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path "_internal") { Remove-Item "_internal" -Recurse -Force -ErrorAction SilentlyContinue }

# Verify standard libraries are loadable
& $pyExe $pyBaseArgs -c "import tkinter; import _tkinter; print('Tkinter OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: System Python does not appear to have Tkinter installed properly." -ForegroundColor Yellow
}

# Step 2.5: Verify Qt Designer (Standalone)
Write-Host "`n[2.5/5] Verify Qt Designer..." -ForegroundColor Cyan
$qtDesignerPath = "Qt Designer\designer.exe"
if (-not (Test-Path $qtDesignerPath)) {
     Write-Host "Qt Designer not found locally. Attempting download..." -ForegroundColor Yellow
     try {
        $downloadUrl = "https://github.com/walidroid/thonnySc/releases/download/qt-designer/qt-designer.zip"
        Invoke-WebRequest $downloadUrl -OutFile "qt-designer.zip"
        Expand-Archive "qt-designer.zip" -DestinationPath "Qt Designer" -Force
        Remove-Item "qt-designer.zip" -Force
     } catch {
        Write-Host "Failed to download Qt Designer: $_" -ForegroundColor Red
     }
}

# Step 2.6: Install Language Server Dependencies
Write-Host "`n[2.6/5] Installing Dependencies..." -ForegroundColor Cyan

Write-Host "Installing requirements..."
if (Test-Path "requirements.txt") {
    & $pyExe $pyBaseArgs -m pip install -r requirements.txt --no-warn-script-location
}

Write-Host "Installing ruff..."
& $pyExe $pyBaseArgs -m pip install ruff --no-warn-script-location

Write-Host "Installing PyQt5..."
& $pyExe $pyBaseArgs -m pip install PyQt5 --no-warn-script-location

Write-Host "Installing esptool..."
& $pyExe $pyBaseArgs -m pip install esptool>=4.0 --no-warn-script-location

Write-Host "Installing jedi..."
& $pyExe $pyBaseArgs -m pip install "jedi>=0.19.0" --no-warn-script-location

Write-Host "Installing serial port packages..."
& $pyExe $pyBaseArgs -m pip install pyserial>=3.5 "adafruit-board-toolkit>=1.1.0" --no-warn-script-location

Write-Host "Installing thonny-autosave..."
& $pyExe $pyBaseArgs -m pip install thonny-autosave --no-deps --no-warn-script-location

Write-Host "Installing numpy..."
& $pyExe $pyBaseArgs -m pip install numpy --no-warn-script-location

# Verify critical packages
$verCheck = & $pyExe $pyBaseArgs -c "import ruff, PyQt5.uic, esptool, jedi, serial, numpy; print('All Good')" 2>$null
if ($verCheck -eq "All Good") {
    Write-Host "Dependency verification successful" -ForegroundColor Green
} else {
    Write-Host "Warning: Some dependencies might be missing." -ForegroundColor Yellow
}

# Step 2.7: Clean up problematic plugins
Write-Host "`n[2.7/5] Cleaning up incompatible plugins..." -ForegroundColor Cyan
if (Test-Path "thonnycontrib\thonny_friendly") {
    Remove-Item "thonnycontrib\thonny_friendly" -Recurse -Force
}

# Step 2.8: Remove unused locale directories
Write-Host "`n[2.8/5] Removing unused locale directories..." -ForegroundColor Cyan
$localeDir = "thonny\locale"
if (Test-Path $localeDir) {
    $keepDirs = @("fr_FR", "en_US")
    Get-ChildItem $localeDir -Directory | Where-Object { $_.Name -notin $keepDirs } | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force
    }
}

# Step 3: Build with PyInstaller
Write-Host "`n[3/5] Building with PyInstaller..." -ForegroundColor Cyan

Write-Host "Installing PyInstaller..."
& $pyExe $pyBaseArgs -m pip install pyinstaller --no-warn-script-location

Write-Host "Running PyInstaller..."
& $pyExe $pyBaseArgs -m PyInstaller thonny.spec

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
    Write-Host "Copied local plugins to $dest"
}

# Copy launcher script
Copy-Item "launch_thonny.py" -Destination "dist"
Write-Host "Copied launch_thonny.py to dist"

# Step 4: Build Installer with Inno Setup
Write-Host "`n[4/5] Building Installer with Inno Setup..." -ForegroundColor Cyan
$innoPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"

if (Test-Path $innoPath) {
    & $innoPath "installer.iss"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installer built successfully!" -ForegroundColor Green
        Write-Host "Distribution ready at: $PSScriptRoot\output" -ForegroundColor Cyan
    } else {
        Write-Host "Installer compilation failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Inno Setup not found at: $innoPath" -ForegroundColor Yellow
    Write-Host "Please install Inno Setup 6 from https://jrsoftware.org/isinfo.php"
    
    if ($env:CI -eq "true") {
        Write-Host "CI environment detected - failing build due to missing compiler" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "Build prepared in dist\Thonny but installer not created." -ForegroundColor Yellow
        Write-Host "Distribution ready at: $PSScriptRoot\dist\Thonny" -ForegroundColor Cyan
    }
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
