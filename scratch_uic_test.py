import sys

# Define patch logic
_QT_METHOD_SIGNATURES = {'setText': (1, 1, 'setText(text: str)')}
_TARGET_CLASSES = ['QWidget', 'QLabel', 'QLineEdit']

def _make_safe_method(method_name, original_method, min_args, max_args, signature):
    def _safe(self, *args, **kwargs):
        n = len(args) + len(kwargs)
        if n < min_args or n > max_args:
            raise TypeError(f"mock TypeError: {min_args} to {max_args} args")
        return original_method(self, *args, **kwargs)
    _safe.__name__ = method_name
    return _safe

def _patch_module(module):
    for class_name in _TARGET_CLASSES:
        original_cls = getattr(module, class_name, None)
        if not original_cls: continue
        overrides = {}
        for method_name, (min_a, max_a, sig) in _QT_METHOD_SIGNATURES.items():
            original_method = getattr(original_cls, method_name, None)
            if not original_method: continue
            overrides[method_name] = _make_safe_method(method_name, original_method, min_a, max_a, sig)
        if not overrides: continue
        safe_cls = type(class_name, (original_cls,), overrides)
        safe_cls.__module__ = module.__name__
        try: setattr(module, class_name, safe_cls)
        except Exception: pass

class _PyQt5WidgetsSafetyFinder:
    def find_module(self, fullname, path=None):
        if fullname == "PyQt5.QtWidgets" and fullname not in sys.modules: return self
        return None
    def load_module(self, fullname):
        try: sys.meta_path.remove(self)
        except ValueError: pass
        import importlib
        mod = importlib.import_module(fullname)
        _patch_module(mod)
        return mod

sys.meta_path.insert(0, _PyQt5WidgetsSafetyFinder())

import tempfile
import PyQt5.QtWidgets as qw
import PyQt5.uic as uic

ui_content = b'''<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <widget class="QWidget" name="centralwidget">
   <widget class="QLabel" name="label">
   </widget>
  </widget>
 </widget>
</ui>'''

with tempfile.NamedTemporaryFile(delete=False, suffix='.ui') as f:
    f.write(ui_content)
    test_ui = f.name

app = qw.QApplication([])
window = uic.loadUi(test_ui)
label = window.label

print('Imported QLabel:', qw.QLabel)
print('Loaded label type:', type(label))

try:
    label.setText('test', 123)
    print('Failed to catch error! Native crash would happen here in Qt.')
except TypeError as e:
    print('Caught successfully:', e)
except Exception as e:
    print('Other error:', type(e))
