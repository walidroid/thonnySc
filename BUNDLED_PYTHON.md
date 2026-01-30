# ThonnySc - Bundled Python Setup

## What Changed

ThonnySc now bundles a **Python 3.13 embeddable package** to enable standalone distribution without requiring users to have Python installed.

### Architecture

```
ThonnySc/
├── Thonny.exe              ← PyInstaller frozen frontend
├── _internal/              ← PyInstaller internal resources
├── Python/                 ← Bundled Python interpreter (NEW!)
│   ├── python.exe         ← Backend uses this
│   ├── python313.dll
│   ├── Lib/
│   ├── Scripts/           ← Contains pip
│   └── thonny_python.ini  ← Marker file
└── wheels/                 ← Offline dependencies
```

## Building Locally

### Option 1: Using Build Script (Recommended)

```powershell
# Run the automated build script
.\build.ps1
```

This script will:
1. Download Python 3.13.1 embeddable package
2. Configure it (marker file, site packages, pip)
3. Build with PyInstaller
4. Create installer with Inno Setup

### Option 2: Manual Steps

```powershell
# 1. Download Python embeddable
$url = "https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-amd64.zip"
Invoke-WebRequest $url -Out "python-embed.zip"
Expand-Archive "python-embed.zip" -DestinationPath "Python"

# 2. Create marker file
New-Item "Python\thonny_python.ini" -ItemType File

# 3. Enable site packages
$pthFile = Get-ChildItem "Python\python*._pth" | Select-Object -First 1
Add-Content $pthFile.FullName "`nimport site"

# 4. Install pip
Invoke-WebRequest "https://bootstrap.pypa.io/get-pip.py" -Out "get-pip.py"
.\Python\python.exe get-pip.py

# 5. Build
pyinstaller thonny.spec

# 6. Create installer
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /DMyAppVersion=1.0.0 installer.iss
```

## Testing

After installation, verify:

1. **Backend starts correctly**
   - Launch ThonnySc
   - Check `AppData\Roaming\Thonny\default\frontend.log`
   - Should show: `Using bundled Python: C:\...\ThonnySc\Python\python.exe`

2. **File operations work**
   - Open a Python file
   - Run a script: `print("Hello")`
   - Verify no "got '' instead of 'OK'" error

3. **Package manager works**
   - Tools → Manage packages
   - Try installing a package

## GitHub Actions Build

The workflow automatically:
- Downloads Python 3.13.1 embeddable
- Configures it with marker file and pip
- Builds PyInstaller bundle
- Creates installer
- Uploads as artifact

## Troubleshooting

### "Backend failed to start"

Check `AppData\Roaming\Thonny\default\backend.log` for errors.

Common issues:
- Python directory missing → Reinstall
- python.exe not found → Check `Python\python.exe` exists
- Permission errors → Run as administrator

### "Could not find bundled Python"

The code checks for: `{app_dir}\Python\python.exe`

Verify structure:
```
ThonnySc\
├── Thonny.exe
└── Python\
    └── python.exe  ← Must exist here
```

### Large installer size

Expected: ~200-250 MB
- PyInstaller bundle: ~150 MB  
- Python embeddable: ~50 MB
- Wheels: ~20 MB

This is normal for standalone Python IDEs.

## Files Modified

1. **cp_front.py** - Detects bundled Python when frozen
2. **installer.iss** - Includes Python directory
3. **build-exe.yml** - Downloads and configures Python
4. **build.ps1** - Local build automation script

## References

- [Python Embeddable Package](https://docs.python.org/3/using/windows.html#windows-embeddable)
- [PyInstaller Frozen Apps](https://pyinstaller.org/en/stable/runtime-information.html)
- [Thonny Architecture](https://github.com/thonny/thonny/wiki)
