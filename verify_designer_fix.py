import os
import sys

# Setup path to import local_plugins
sys.path.append(os.path.join(os.getcwd(), "local_plugins"))

# Mock Thonny dependencies to allow importing the plugin
import types
thonny = types.ModuleType("thonny")
thonny.get_workbench = lambda: None
thonny.languages = types.ModuleType("thonny.languages")
thonny.languages.tr = lambda x: x
thonny.ui_utils = types.ModuleType("thonny.ui_utils")
thonny.ui_utils.select_sequence = lambda x, y: None
thonny.ui_utils.askopenfilename = lambda **kwargs: None
sys.modules["thonny"] = thonny
sys.modules["thonny.languages"] = thonny.languages
sys.modules["thonny.ui_utils"] = thonny.ui_utils

# Import the plugin
from thonnycontrib.tunisiaschools import find_qt_designer

print("Searching for Qt Designer...")
path = find_qt_designer()

if path and os.path.exists(path):
    print(f"SUCCESS: Found Qt Designer at: {path}")
else:
    print(f"FAILURE: Could not find Qt Designer. Result: {path}")
