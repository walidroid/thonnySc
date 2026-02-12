import sys
import os

# Auto-detect and set Tcl/Tk library paths if needed
def setup_tcl_tk():
    """Configure Tcl/Tk environment for tkinter"""
    if sys.platform == "win32":
        # Try to find Tcl/Tk in common Python installation locations
        python_dir = os.path.dirname(sys.executable)
        tcl_dir = os.path.join(python_dir, "tcl")
        
        if os.path.exists(tcl_dir):
            # Find tcl8.x and tk8.x directories
            for item in os.listdir(tcl_dir):
                item_path = os.path.join(tcl_dir, item)
                if os.path.isdir(item_path):
                    if item.startswith("tcl8.") and "TCL_LIBRARY" not in os.environ:
                        os.environ["TCL_LIBRARY"] = item_path
                        print(f"DEBUG: Set TCL_LIBRARY={item_path}")
                    elif item.startswith("tk8.") and "TK_LIBRARY" not in os.environ:
                        os.environ["TK_LIBRARY"] = item_path
                        print(f"DEBUG: Set TK_LIBRARY={item_path}")

# Set up Tcl/Tk before importing thonny
setup_tcl_tk()

# Absolute path to this project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

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
