# Diagnostic script to test bundled Python
# Run this on the test computer to verify the Python embeddable package

import os
import sys

print("=" * 60)
print("BUNDLED PYTHON DIAGNOSTIC")
print("=" * 60)

# Get paths
if getattr(sys, 'frozen', False):
    app_dir = os.path.dirname(sys.executable)
    bundled_python = os.path.join(app_dir, "Python", "python.exe")
    print(f"\nRunning as frozen app: YES")
    print(f"App directory: {app_dir}")
    print(f"Bundled Python path: {bundled_python}")
else:
    bundled_python = "Python\\python.exe"
    print(f"\nRunning as frozen app: NO")
    print(f"Using relative path: {bundled_python}")

print(f"\nBundled Python exists: {os.path.exists(bundled_python)}")

if os.path.exists(bundled_python):
    python_dir = os.path.dirname(bundled_python)
    
    print(f"\nContents of {python_dir}:")
    for item in sorted(os.listdir(python_dir)):
        path = os.path.join(python_dir, item)
        if os.path.isdir(path):
            print(f"  [DIR]  {item}")
        else:
            size_kb = os.path.getsize(path) / 1024
            print(f"  [FILE] {item} ({size_kb:.1f} KB)")
    
    # Test importing modules
    print("\n" + "=" * 60)
    print("MODULE IMPORT TESTS")
    print("=" * 60)
    
    import subprocess
    
    test_modules = [
        "sys",
        "os",
        "sched",  # This was missing in error logs
        "tkinter",
        "site",
        "pip",
    ]
    
    for module in test_modules:
        try:
            result = subprocess.run(
                [bundled_python, "-c", f"import {module}; print('OK')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "OK" in result.stdout:
                print(f"  ✓ {module:15s} - OK")
            else:
                print(f"  ✗ {module:15s} - FAILED")
                if result.stderr:
                    print(f"    Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"  ✗ {module:15s} - ERROR: {e}")
    
    # Test running Thonny backend launcher
    print("\n" + "=" * 60)
    print("BACKEND LAUNCHER TEST")
    print("=" * 60)
    
    if getattr(sys, 'frozen', False):
        launcher_path = os.path.join(app_dir, "_internal", "thonny", "plugins", "cpython_backend", "cp_launcher.py")
    else:
        launcher_path = "thonny\\plugins\\cpython_backend\\cp_launcher.py"
    
    print(f"\nLauncher path: {launcher_path}")
    print(f"Launcher exists: {os.path.exists(launcher_path)}")
    
    if os.path.exists(launcher_path):
        print("\nTrying to import thonny from bundled Python...")
        try:
            result = subprocess.run(
                [bundled_python, "-c", "import thonny; print('Thonny version:', thonny.version.version)"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"  ✓ SUCCESS: {result.stdout.strip()}")
            else:
                print(f"  ✗ FAILED:")
                print(f"    stdout: {result.stdout}")
                print(f"    stderr: {result.stderr}")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")

else:
    print("\n✗ Bundled Python not found!")
    print("  The installer may not have included the Python directory.")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
