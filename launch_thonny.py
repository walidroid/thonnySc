import sys
import os

# Auto-detect and set Tcl/Tk library paths if needed
def setup_tcl_tk():
    """Configure Tcl/Tk environment for tkinter in frozen (PyInstaller) bundles."""
    if sys.platform != "win32":
        return

    # Already set — nothing to do
    if "TCL_LIBRARY" in os.environ and "TK_LIBRARY" in os.environ:
        return

    # Candidate base directories to search
    candidates = []

    # 1. PyInstaller frozen bundle: _internal folder next to the EXE
    if getattr(sys, "frozen", False):
        internal_dir = os.path.join(os.path.dirname(sys.executable), "_internal")
        if os.path.isdir(internal_dir):
            candidates.append(internal_dir)

    # 2. Directory of sys.executable (standard Python install or _internal itself)
    candidates.append(os.path.dirname(sys.executable))
    real_dir = os.path.dirname(os.path.realpath(sys.executable))
    if real_dir not in candidates:
        candidates.append(real_dir)

    for base_dir in candidates:
        # PyInstaller layout: tcl8/ and _tk_data/ directly inside _internal
        # Standard layout: tcl/tcl8.x/ and tcl/tk8.x/ inside python dir
        search_dirs = [base_dir, os.path.join(base_dir, "tcl")]

        for search_dir in search_dirs:
            if not os.path.isdir(search_dir):
                continue
            for item in os.listdir(search_dir):
                item_path = os.path.join(search_dir, item)
                if not os.path.isdir(item_path):
                    continue
                # Match tcl8, tcl8.6, tcl8.x etc.
                if item.startswith("tcl8") and "TCL_LIBRARY" not in os.environ:
                    os.environ["TCL_LIBRARY"] = item_path
                # Match tk8, tk8.6, _tk_data etc.
                if (item.startswith("tk8") or item == "_tk_data") and "TK_LIBRARY" not in os.environ:
                    os.environ["TK_LIBRARY"] = item_path

        if "TCL_LIBRARY" in os.environ and "TK_LIBRARY" in os.environ:
            break

# Set up Tcl/Tk before importing thonny
setup_tcl_tk()


# Absolute path to this project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Ensure site-packages directories are in sys.path
# This is critical for packages like pyserial and adafruit-board-toolkit
# which may not be found if the Python installation config is broken
for sp_dir in [
    os.path.join(project_root, "Lib", "site-packages"),
    os.path.join(project_root, "Python", "Lib", "site-packages"),
]:
    if os.path.isdir(sp_dir) and sp_dir not in sys.path:
        sys.path.insert(1, sp_dir)
        print(f"DEBUG: Added site-packages: {sp_dir}")

print(f"DEBUG: Project root: {project_root}")
print(f"DEBUG: sys.path: {sys.path[:3]}...")

try:
    import thonny
    print(f"DEBUG: thonny path: {thonny.__file__}")
    from thonny import launch
    sys.exit(launch())
except ImportError as e:
    print(f"Error starting Thonny: {e}")
    if not os.path.exists(os.path.join(project_root, "thonny")):
         print(f"CRITICAL: 'thonny' directory NOT found in {project_root}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
