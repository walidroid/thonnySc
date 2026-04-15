"""
pyqt5_backend.py – Thonny backend plugin for PyQt5 safety.

When a PyQt5/Qt C++ method is called with wrong arguments (e.g. setText("x", y)),
the backend process crashes natively (exit code 0xC0000409) before Python can
produce any traceback.

The previous approach of using setattr() on sip-wrapped C++ classes silently
fails because sip types are read-only — the patch never actually applied.

This version works by creating Python *subclasses* of each Qt widget class that
override the dangerous methods with argument-count validators. These subclasses
then replace the originals inside the PyQt5.QtWidgets module, so any user code
doing `from PyQt5.QtWidgets import QLabel` (or similar) automatically gets the
safe version. When wrong arguments are passed, Python raises a proper TypeError
with a full traceback and line number — before Qt's C++ layer is ever touched.
"""


# ---------------------------------------------------------------------------
# Argument-count rules for commonly misused Qt widget methods.
# All counts EXCLUDE `self`.
# ---------------------------------------------------------------------------
_QT_METHOD_SIGNATURES = {
    "setText":                   (1, 1, "setText(text: str)"),
    "setPlainText":              (1, 1, "setPlainText(text: str)"),
    "setHtml":                   (1, 1, "setHtml(html: str)"),
    "setTitle":                  (1, 1, "setTitle(title: str)"),
    "setWindowTitle":            (1, 1, "setWindowTitle(title: str)"),
    "setToolTip":                (1, 1, "setToolTip(text: str)"),
    "setStatusTip":              (1, 1, "setStatusTip(text: str)"),
    "setWhatsThis":              (1, 1, "setWhatsThis(text: str)"),
    "setPlaceholderText":        (1, 1, "setPlaceholderText(text: str)"),
    "setPrefix":                 (1, 1, "setPrefix(prefix: str)"),
    "setSuffix":                 (1, 1, "setSuffix(suffix: str)"),
    "setFlat":                   (1, 1, "setFlat(flat: bool)"),
    "setChecked":                (1, 1, "setChecked(checked: bool)"),
    "setEnabled":                (1, 1, "setEnabled(enabled: bool)"),
    "setVisible":                (1, 1, "setVisible(visible: bool)"),
    "setReadOnly":               (1, 1, "setReadOnly(readOnly: bool)"),
    "setMaxLength":              (1, 1, "setMaxLength(length: int)"),
    "setMaximum":                (1, 1, "setMaximum(value: int)"),
    "setMinimum":                (1, 1, "setMinimum(value: int)"),
    "setValue":                  (1, 1, "setValue(value: int)"),
    "setRange":                  (2, 2, "setRange(minimum: int, maximum: int)"),
    "setAlignment":              (1, 1, "setAlignment(alignment)"),
    "setFont":                   (1, 1, "setFont(font: QFont)"),
    "setStyleSheet":             (1, 1, "setStyleSheet(styleSheet: str)"),
    "setFixedSize":              (1, 2, "setFixedSize(width: int, height: int)  or  setFixedSize(QSize)"),
    "setFixedWidth":             (1, 1, "setFixedWidth(width: int)"),
    "setFixedHeight":            (1, 1, "setFixedHeight(height: int)"),
    "resize":                    (1, 2, "resize(width: int, height: int)  or  resize(QSize)"),
    "move":                      (1, 2, "move(x: int, y: int)  or  move(QPoint)"),
    "addItem":                   (1, 3, "addItem(text: str[, icon[, userData]])"),
    "addItems":                  (1, 1, "addItems(texts: list)"),
    "insertItem":                (2, 4, "insertItem(index: int, text: str[, icon[, userData]])"),
    "setCurrentIndex":           (1, 1, "setCurrentIndex(index: int)"),
    "setCurrentText":            (1, 1, "setCurrentText(text: str)"),
    "setPixmap":                 (1, 1, "setPixmap(pixmap: QPixmap)"),
    "setScaledContents":         (1, 1, "setScaledContents(scaled: bool)"),
    "setWordWrap":               (1, 1, "setWordWrap(on: bool)"),
    "setColumnCount":            (1, 1, "setColumnCount(columns: int)"),
    "setRowCount":               (1, 1, "setRowCount(rows: int)"),
    "setHorizontalHeaderLabels": (1, 1, "setHorizontalHeaderLabels(labels: list)"),
    "setVerticalHeaderLabels":   (1, 1, "setVerticalHeaderLabels(labels: list)"),
}

# Qt widget classes to protect
_TARGET_CLASSES = [
    "QWidget", "QLabel", "QLineEdit", "QPushButton", "QTextEdit",
    "QPlainTextEdit", "QCheckBox", "QRadioButton", "QComboBox",
    "QSpinBox", "QDoubleSpinBox", "QSlider", "QDial",
    "QGroupBox", "QTabWidget", "QListWidget", "QTableWidget",
    "QTreeWidget", "QProgressBar", "QLCDNumber",
]


def _make_safe_method(method_name, original_method, min_args, max_args, signature):
    """
    Build a Python method that validates argument count, then calls the original
    sip/C++ method.  Capturing `original_method` in the closure lets us call
    QLabel.setText(self, ...) even after the module-level name is replaced.
    """
    def _safe(self, *args, **kwargs):
        n = len(args) + len(kwargs)
        if n < min_args or n > max_args:
            expected = (
                f"exactly {min_args}"
                if min_args == max_args
                else f"{min_args} to {max_args}"
            )
            raise TypeError(
                f"{type(self).__name__}.{method_name}() takes {expected} "
                f"argument(s) but {n} {'was' if n == 1 else 'were'} given.\n"
                f"  Correct usage: {signature}"
            )
        return original_method(self, *args, **kwargs)

    _safe.__name__ = method_name
    _safe.__qualname__ = f"<pyqt5_safe>.{method_name}"
    return _safe


def _patch_pyqt5_widgets(module):
    """
    Called automatically right after `PyQt5.QtWidgets` is imported.

    For each target class (QLabel, QLineEdit, …) we:
      1. Grab the original sip-wrapped C++ class from the module.
      2. Build a dict of safe Python override methods.
      3. Create a new Python subclass:  SafeQLabel(QLabel): ...
      4. Replace the name inside the module so downstream `from … import QLabel`
         gets the safe subclass.
    """
    for class_name in _TARGET_CLASSES:
        original_cls = getattr(module, class_name, None)
        if original_cls is None:
            continue

        # Build only the overrides that the class actually has
        overrides = {}
        for method_name, (min_a, max_a, sig) in _QT_METHOD_SIGNATURES.items():
            original_method = getattr(original_cls, method_name, None)
            if original_method is None:
                continue
            overrides[method_name] = _make_safe_method(
                method_name, original_method, min_a, max_a, sig
            )

        if not overrides:
            continue

        # Create a Python subclass — Python subclasses DO allow attribute
        # assignment, unlike the raw sip C++ types.
        safe_cls = type(class_name, (original_cls,), overrides)
        safe_cls.__module__ = module.__name__

        # Replace inside the module.  Future `from PyQt5.QtWidgets import XYZ`
        # will now get the safe subclass automatically.
        try:
            setattr(module, class_name, safe_cls)
        except Exception:
            pass  # extremely unlikely; log silently


def load_plugin():
    from thonny.plugins.cpython_backend import get_backend
    backend = get_backend()
    backend.add_import_handler("PyQt5.QtWidgets", _patch_pyqt5_widgets)
