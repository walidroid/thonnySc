import sys
import os
import pkgutil
import importlib

# Mimic thonny's path setup from thonny/workbench.py
project_root = os.getcwd() # Assumption: running from thonnySc
local_plugins_dir = os.path.join(project_root, "local_plugins")

print(f"Adding {local_plugins_dir} to sys.path")
sys.path.insert(0, local_plugins_dir)

# Also add site-packages if needed, but we want to test local_plugins priority
# We simulate the environment where thonny is installed or available
# If running with local python, we might need to add current dir to path to find 'thonny' package if needed
# But here we focus on thonnycontrib

try:
    import thonnycontrib
    print(f"Imported thonnycontrib. Path: {thonnycontrib.__path__}")
except ImportError:
    print("Could not import thonnycontrib. Creating dummy if needed for test?")
    # In real Thonny, thonnycontrib might be in site-packages. 
    # Here we hope local_plugins/thonnycontrib is sufficient to be a namespace package
    pass

if 'thonnycontrib' in sys.modules:
    print("Iterating modules in thonnycontrib:")
    for finder, module_name, ispkg in pkgutil.iter_modules(thonnycontrib.__path__, "thonnycontrib."):
        print(f"Found: {module_name} (pkg={ispkg})")
        if "thonny_autosave" in module_name:
             try:
                m = importlib.import_module(module_name)
                print(f"  Imported {module_name} from {m.__file__}")
                if hasattr(m, "load_plugin"):
                    print(f"  Has load_plugin()")
             except Exception as e:
                print(f"  Failed to import: {e}")
else:
    print("thonnycontrib not loaded")
