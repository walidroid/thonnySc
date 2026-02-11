import sys
import os

# Add current directory to sys.path so 'thonny' package can be found
# This overrides restrictions from python._pth if present
sys.path.append(os.getcwd())

try:
    from thonny import launch
    sys.exit(launch())
except ImportError as e:
    print(f"Error starting Thonny: {e}")
    # checking if thonny exists
    if not os.path.exists("thonny"):
         print("CRITICAL: 'thonny' directory not found in current location.")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
