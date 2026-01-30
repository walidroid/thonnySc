# IMPORTANT: Plugin Cleanup Required

## friendly_launcher Plugin Removal

The `thonnycontrib.backend.friendly_launcher` plugin needs to be **uninstalled** on systems where ThonnySc is installed.

### Why?

This plugin:
- Is installed in **system Python** (not bundled Python)
- Tries to load in the **frontend** process (wrong location)
- Causes warning: `Failed loading plugin thonnycontrib.backend.friendly_launcher`
- Is **redundant** - the `error_translator` plugin already provides French error translation

### How to Remove

On each computer where ThonnySc is installed, run:

```cmd
pip uninstall thonny-friendly-backend
```

Or if the package has a different name:

```cmd
pip uninstall friendly-traceback-backend
pip uninstall thonny-friendly
```

### Verification

After removal, the warning should disappear from the logs:
```
✗ Warning: Failed loading plugin thonnycontrib.backend.friendly_launcher  ← Should disappear
✓ INFO thonnycontrib.error_translator: Error translator plugin loaded     ← Should remain
```

### Alternative: Ignore the Warning

If you can't access other computers to uninstall:
- The warning is harmless - Thonny continues to work
- The `error_translator` plugin provides the same functionality
- Users can safely ignore this warning

## Summary of Changes Made

### ✅ Fixed: Qt Designer Launcher

**File**: `local_plugins/thonnycontrib/tunisiaschools/__init__.py`

**Changes**:
1. Added `find_qt_designer()` helper function
   - Checks for bundled Qt Designer first
   - Scans common installation directories
   - Uses `shutil.which()` to find in PATH

2. Rewrote `open_in_designer()` function
   - Fixed missing comma bug
   - Fixed logic error (return inside loop)
   - Added user-friendly error messages
   - Proper exception handling

3. Added `sys` import

**Result**: Qt Designer button now:
- Works correctly when Qt Designer is installed
- Shows helpful error message when not found
- Provides installation instructions to users

### ✅ Fixed: Language Server Subprocess

**File**: `thonny/running.py`

**Changes**:
1. Modified `get_front_interpreter_for_subprocess()`
   - Detects frozen mode (PyInstaller)
   - Uses bundled `Python/python.exe` instead of `Thonny.exe`

**Result**: Ruff language server and other subprocesses now work correctly

### ✅ Fixed: Backend Detection

**File**: `thonny/plugins/cpython_frontend/cp_front.py`

**Changes**:
1. Modified `get_default_cpython_executable_for_backend()`
   - Detects frozen mode
   - Uses bundled Python for backend

**Result**: Backend starts correctly with bundled Python

## Next Build

When you rebuild the installer:
1. All these fixes will be included
2. Language servers will work
3. Qt Designer button will show proper errors if not installed
4. Backend will use bundled Python correctly

## Optional: Bundle Qt Designer

To make ThonnySc completely standalone, you can bundle Qt Designer:

1. Download Qt Designer standalone: https://build-system.fman.io/qt-designer-download
2. Extract to `Qt Designer/` folder in project
3. Update `installer.iss`:
   ```iss
   Source: "Qt Designer\*"; DestDir: "{app}\Qt Designer"; Flags: ignoreversion recursesubdirs
   ```

Then Qt Designer will work on all computers without installation!
