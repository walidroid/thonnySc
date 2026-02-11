import sys
import os

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
