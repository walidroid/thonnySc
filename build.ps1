# ThonnySc Build Script
# This script downloads Python embeddable package and builds the installer locally

Write-Host "=== ThonnySc Build Script ===" -ForegroundColor Green

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
$version = "1.0.0"
$innoPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (Test-Path $innoPath) {
    & $innoPath /DMyAppVersion=$version installer.iss
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
if (Test-Path "output\ThonnySc_v$version.exe") {
    $size = (Get-Item "output\ThonnySc_v$version.exe").Length / 1MB
    Write-Host "  Installer: output\ThonnySc_v$version.exe ($($size.ToString('F2')) MB)" -ForegroundColor White
}

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Test the installer: .\output\ThonnySc_v$version.exe"
Write-Host "  2. Verify backend starts correctly"
Write-Host "  3. Try opening and running Python files"
