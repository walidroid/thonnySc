import re

path = r'c:\Users\Admin\Desktop\thonnySc\thonny\plugins\cpython_backend\cp_back.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the call
text = text.replace('self._install_pyqt5_safety_hook()', 'self._install_safe_excepthook()')

# Build the new hook string
new_hook = '''    def _install_safe_excepthook(self):
        """
        By default, if an unhandled Python exception occurs inside a PyQt5 C++ slot
        (like passing `setText('text', 123)`), PyQt5 catches it, calls sys.excepthook,
        and if sys.excepthook is the default sys.__excepthook__, PyQt5 intentionally
        calls abort() or qFatal(). This produces a native STATUS_STACK_BUFFER_OVERRUN
        (exit code 0xC0000409) crash, hiding the actual Python TypeError from the user.
        
        By installing a custom sys.excepthook (even one that just delegates to the
        original), we signal to PyQt5 that we are handling the exception ourselves.
        This prevents the native crash, and Thonny cleanly intercepts the traceback
        written to sys.stderr to show the user exactly where their code failed.
        """
        def safe_excepthook(exc_type, exc_value, exc_traceback):
            import sys
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        import sys
        sys.excepthook = safe_excepthook

'''

# Extract the big chunk we want to replace using regex.
pattern = re.compile(r'    def _install_pyqt5_safety_hook\(self\):.*?    def _fetch_next_incoming_message', re.DOTALL)
text, count = pattern.subn(new_hook + '    def _fetch_next_incoming_message', text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print(f'Replaced {count} instances of the hook.')
