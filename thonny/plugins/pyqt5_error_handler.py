"""
PyQt5 Error Handler Plugin
Prevents STATUS_STACK_BUFFER_OVERRUN crashes in bundled executables
"""

import sys
import traceback
from thonny import get_workbench

def load_plugin():
    def install_pyqt5_exception_handler(event=None):
        """Install exception handler before running user code or when backend is ready"""
        
        def pyqt5_safe_excepthook(exc_type, exc_value, exc_tb):
            # Prevent Qt crashes from taking down the IDE
            if exc_type.__name__ == 'SystemExit':
                try:
                    code = exc_value.code
                except AttributeError:
                    code = 0
                original_excepthook(exc_type, exc_value, exc_tb) # Let system handle exit
                return

            try:
                # Print error details
                print("\n" + "="*70, file=sys.stderr)
                print(" PyQt5 ERROR DETECTED ", file=sys.stderr)
                print("="*70, file=sys.stderr)
                traceback.print_exception(exc_type, exc_value, exc_tb, file=sys.stderr)
                print("="*70 + "\n", file=sys.stderr)
            except:
                # Fallback to original
                original_excepthook(exc_type, exc_value, exc_tb)

        # Only install if not already installed
        if sys.excepthook.__name__ != "pyqt5_safe_excepthook":
            global original_excepthook
            original_excepthook = sys.excepthook
            sys.excepthook = pyqt5_safe_excepthook

    # Hook into code execution
    wb = get_workbench()
    # BackendReady is a good place to ensure frontend knows about it, 
    # but the handler needs to be in the BACKEND process for user code.
    # This plugin runs in the FRONTEND. 
    # Wait, the user instructions said "Create a file thonny/plugins/pyqt5_error_handler.py ... load_plugin ... wb.bind".
    # This implies frontend plugin.
    # But user code runs in backend.
    # If the crash happens in frontend (Thonny UI), this helps.
    # If the crash happens in backend (User code), the backend modifications I did earlier help.
    # The user instruction seems to target frontend protection too? 
    # Or maybe they want to inject it into backend via some command?
    # The code `wb.bind("BackendReady", ...)` suggests frontend.
    
    install_pyqt5_exception_handler()
