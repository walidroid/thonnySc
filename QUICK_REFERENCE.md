# Quick Reference: Portable Setup

## Launch Commands

### Windows
```cmd
# Method 1: Batch file
RunThonny417.bat

# Method 2: Direct Python
py -3 launch_thonny.py

# Method 3: With specific Python
python launch_thonny.py
```

### Linux/macOS
```bash
# Method 1: Shell script
chmod +x run_thonny.sh
./run_thonny.sh

# Method 2: Direct Python
python3 launch_thonny.py
```

## Files You Can Modify

### Safe to Edit (Take Effect Immediately)
- `thonny/**/*.py` - All Python source files
- `local_plugins/**/*.py` - Custom plugins
- `data/**` - Resources, icons, themes
- `requirements.txt` - Python dependencies

### Requires Rebuild
- `thonny.spec` - PyInstaller configuration
- `installer.iss` - Inno Setup installer script
- `build.ps1` - Build automation script

## Portable Fixes Applied

✅ **Auto-detection:** Tcl/Tk libraries found automatically  
✅ **Cross-platform:** Works on Windows, Linux, macOS  
✅ **CI-ready:** GitHub Actions compatible  
✅ **No hardcoding:** All paths detected at runtime  
✅ **Single-instance:** Prevents multiple windows  
✅ **Safe loading:** Only opens files, not directories  

## GitHub Workflows

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| `test-portable.yml` | Test portable setup | Every push |
| `build.yml` | Build installer | Every push |
| `build-exe.yml` | Build executable | Manual (workflow_dispatch) |

## Troubleshooting

**Problem:** `Can't find init.tcl`  
**Solution:** Python missing tkinter → reinstall Python with tkinter support

**Problem:** `FileNotFoundError: C:\`  
**Solution:** Fixed in `thonny/editors.py` → update your repository

**Problem:** Multiple windows launching  
**Solution:** Fixed in `thonny/__init__.py` → `SINGLE_INSTANCE_DEFAULT = True`

**Problem:** Backend communication error  
**Solution:** Check `working_directory` in `configuration.ini` is valid

## Development Workflow

1. **Edit code** in `thonny/` directory
2. **Test immediately** with `launch_thonny.py`
3. **Commit changes** to Git
4. **Push to GitHub** → CI tests run automatically
5. **Build installer** (optional) via `build-exe.yml` workflow

## Documentation

- `PORTABLE_FIXES.md` - Detailed changelog
- `RUNNING_FROM_SOURCE.md` - Comprehensive guide
- `README.rst` - Project overview
