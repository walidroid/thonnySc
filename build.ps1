param (
    [string]$Version = "1.0.0"
)

# ThonnySc Build Script
# This script downloads Python embeddable package and builds the installer locally

Write-Host "=== ThonnySc Build Script ===" -ForegroundColor Green
Write-Host "Building version: $Version" -ForegroundColor Green
Set-Location -Path $PSScriptRoot

# Step 1: Download Python Embeddable Package
Write-Host "`n[1/5] Downloading Python Embeddable Package..." -ForegroundColor Cyan
$pythonVersion = "3.13.1"
$url = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-embed-amd64.zip"

if (Test-Path "Python\python.exe") {
    Write-Host "Python already exists, skipping download" -ForegroundColor Yellow
} else {
    Write-Host "Downloading from: $url"
    Invoke-WebRequest $url -Out "python-embed.zip"
    Write-Host "Extracting..."
    Expand-Archive "python-embed.zip" -DestinationPath "Python" -Force
    Remove-Item "python-embed.zip"
    Write-Host "Python embeddable package extracted" -ForegroundColor Green
}

# Step 2: Configure Embeddable Python
Write-Host "`n[2/5] Configuring Embeddable Python..." -ForegroundColor Cyan

# Create marker file
New-Item "Python\thonny_python.ini" -ItemType File -Force | Out-Null
Write-Host "Created thonny_python.ini marker file"

# Enable site packages
$pthFile = Get-ChildItem "Python\python*._pth" | Select-Object -First 1
if ($pthFile) {
    $content = Get-Content $pthFile.FullName
    if ($content -notcontains "import site") {
        Add-Content $pthFile.FullName "`nimport site"
        Write-Host "Enabled site packages in $($pthFile.Name)"
    } else {
        Write-Host "Site packages already enabled"
    }
}

# Install pip
if (Test-Path "Python\Scripts\pip.exe") {
    Write-Host "Pip already installed" -ForegroundColor Yellow
} else {
    Write-Host "Installing pip..."
    Invoke-WebRequest "https://bootstrap.pypa.io/get-pip.py" -Out "get-pip.py"
    & ".\Python\python.exe" "get-pip.py" --no-warn-script-location
    Remove-Item "get-pip.py"
    Write-Host "Pip installed successfully" -ForegroundColor Green
}

& ".\Python\python.exe" -m pip install --upgrade pip wheel setuptools --no-warn-script-location

# Step 2.5: Verify Qt Designer
Write-Host "`n[2.5/5] Verifying Qt Designer..." -ForegroundColor Cyan

$qtDesignerPath = "Qt Designer\designer.exe"
if (Test-Path $qtDesignerPath) {
    $qtSize = (Get-Item $qtDesignerPath).Length / 1MB
    Write-Host "Qt Designer found: $qtDesignerPath ($([math]::Round($qtSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "Qt Designer not found locally." -ForegroundColor Yellow
    Write-Host "Attempting to download from GitHub release..." -ForegroundColor Cyan
    
    try {
        $downloadUrl = "https://github.com/walidroid/thonnySc/releases/download/qt-designer/qt-designer.zip"
        Invoke-WebRequest $downloadUrl -Out "qt-designer.zip"
        
        Write-Host "Extracting Qt Designer..."
        # Create directory if it doesn't exist (Expand-Archive usually does this but good to be safe)
        if (-not (Test-Path "Qt Designer")) { New-Item -ItemType Directory -Path "Qt Designer" | Out-Null }
        
        Expand-Archive "qt-designer.zip" -DestinationPath "Qt Designer" -Force
        Remove-Item "qt-designer.zip" -Force
        
        if (Test-Path $qtDesignerPath) {
            Write-Host "Qt Designer downloaded and installed successfully" -ForegroundColor Green
        } else {
            throw "Extraction failed or designer.exe not found"
        }
    } catch {
        Write-Host "Failed to download/install Qt Designer: $_" -ForegroundColor Red
        if ($env:CI -eq "true") {
            # In CI we might want to fail, or just warn if it's optional. 
            # User said "integrated", so let's fail if it's missing in CI? 
            # Or just warn. Let's warn for now to avoid breaking build if release is missing.
            Write-Host "Continuing without Qt Designer..." -ForegroundColor Yellow
        } else {
             $response = Read-Host "Continue without Qt Designer? (y/n)"
             if ($response -ne "y") {
                exit 1
             }
        }
    }
}

# Step 2.6: Install Language Server Dependencies
Write-Host "`n[2.6/5] Installing Language Server Dependencies..." -ForegroundColor Cyan

Write-Host "Installing ruff for code linting..."
& ".\Python\python.exe" -m pip install ruff --no-warn-script-location

if ($LASTEXITCODE -eq 0) {
    Write-Host "Ruff installed successfully" -ForegroundColor Green
    
    # Verify installation
    $ruffCheck = & ".\Python\python.exe" -c "import ruff; print('OK')" 2>$null
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
& ".\Python\python.exe" -m pip install PyQt5 --no-warn-script-location

if ($LASTEXITCODE -eq 0) {
    Write-Host "PyQt5 installed successfully" -ForegroundColor Green
    
    # Verify installation
    $pyqt5Check = & ".\Python\python.exe" -c "from PyQt5.uic import loadUi; print('OK')" 2>$null
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
& ".\Python\python.exe" -m pip install esptool==5.1.0 --no-warn-script-location

if ($LASTEXITCODE -eq 0) {
    Write-Host "esptool installed successfully" -ForegroundColor Green
    
    # Verify installation
    $esptoolCheck = & ".\Python\python.exe" -c "import esptool; print('OK')" 2>$null
    if ($esptoolCheck -eq "OK") {
        Write-Host "esptool verification successful" -ForegroundColor Green
    } else {
        Write-Host "Warning: esptool verification failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: esptool installation failed - ESP32/ESP8266 support unavailable" -ForegroundColor Yellow
}

# Step 2.6.3: Install minny for backend communication
Write-Host "`nInstalling minny for backend communication..."
& ".\Python\python.exe" -m pip install minny --no-warn-script-location

if ($LASTEXITCODE -eq 0) {
    Write-Host "minny installed successfully" -ForegroundColor Green
    
    # Verify installation
    $minnyCheck = & ".\Python\python.exe" -c "import minny; print('OK')" 2>$null
    if ($minnyCheck -eq "OK") {
        Write-Host "minny verification successful" -ForegroundColor Green
    } else {
        Write-Host "Warning: minny verification failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: minny installation failed - Backend may not work" -ForegroundColor Yellow
}

# Step 2.6.4: Install thonny-autosave and missing stdlib dependencies
Write-Host "`nInstalling thonny-autosave and dependencies..."

# Copy sched.py (missing from embeddable python)
try {
    # Try to find sched.py using the python available in PATH (or the one running this script context)
    $schedFile = python -c "import sched; print(sched.__file__)" 2>$null
    
    if ($schedFile -and (Test-Path $schedFile)) {
        Copy-Item $schedFile -Destination "Python\sched.py" -Force
        Write-Host "Copied sched.py from $schedFile" -ForegroundColor Green
    } else {
        # Fallback to a hardcoded path only if dynamic search fails
        $hostSched = "C:\Users\Walid\AppData\Local\Programs\Python\Python313\Lib\sched.py"
        if (Test-Path $hostSched) {
            Copy-Item $hostSched -Destination "Python\sched.py" -Force
            Write-Host "Copied sched.py from hardcoded path" -ForegroundColor Green
        } else {
             Write-Host "Warning: Could not locate sched.py dynamically or at hardcoded path." -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "Warning: Error while trying to locate sched.py: $_" -ForegroundColor Yellow
}

# Install the plugin (no-deps to avoid installing older Thonny version)
& ".\Python\python.exe" -m pip install thonny-autosave --no-deps --no-warn-script-location



$numpyTarget = "numpy"
Write-Host "`nInstalling $numpyTarget..." -ForegroundColor Cyan
& ".\Python\python.exe" -m pip install $numpyTarget --no-warn-script-location
if ($LASTEXITCODE -eq 0) {
    $numpyCheck = & ".\Python\python.exe" -c "import numpy as np; import numpy.linalg; print('OK')" 2>$null
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


# Step 3: Build with PyInstaller
Write-Host "`n[3/5] Building with PyInstaller..." -ForegroundColor Cyan
pyinstaller thonny.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "PyInstaller build completed" -ForegroundColor Green

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
