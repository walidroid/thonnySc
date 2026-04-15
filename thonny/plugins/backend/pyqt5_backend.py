"""
pyqt5_backend.py – Thonny backend plugin for PyQt5 safety.

When a PyQt5/Qt C++ method is called with wrong arguments (e.g. setText("x", y)),
the backend process crashes natively (exit code 0xC0000409) before Python can
produce any traceback. This plugin intercepts the problematic calls at the Python
layer and raises a proper TypeError (with file + line number) before Qt is touched.
"""


# ---------------------------------------------------------------------------
# Argument-count rules for commonly misused Qt widget methods.
# Format: { module_attr_path: (min_args, max_args, description) }
# All counts EXCLUDE `self`.
# ---------------------------------------------------------------------------
_QT_METHOD_SIGNATURES = {
    # QLabel / QLineEdit / QPushButton / QTextEdit …
    "setText":                (1, 1, "setText(text)"),
    "setPlainText":           (1, 1, "setPlainText(text)"),
    "setHtml":                (1, 1, "setHtml(html)"),
    "setTitle":               (1, 1, "setTitle(title)"),
    "setWindowTitle":         (1, 1, "setWindowTitle(title)"),
    "setToolTip":             (1, 1, "setToolTip(text)"),
    "setStatusTip":           (1, 1, "setStatusTip(text)"),
    "setWhatsThis":           (1, 1, "setWhatsThis(text)"),
    "setPlaceholderText":     (1, 1, "setPlaceholderText(text)"),
    "setPrefix":              (1, 1, "setPrefix(prefix)"),
    "setSuffix":              (1, 1, "setSuffix(suffix)"),
    "setLabel":               (1, 1, "setLabel(text)"),
    "setFlat":                (1, 1, "setFlat(flat)"),
    "setChecked":             (1, 1, "setChecked(checked)"),
    "setEnabled":             (1, 1, "setEnabled(enabled)"),
    "setVisible":             (1, 1, "setVisible(visible)"),
    "setReadOnly":            (1, 1, "setReadOnly(readOnly)"),
    "setMaxLength":           (1, 1, "setMaxLength(length)"),
    "setMaximum":             (1, 1, "setMaximum(value)"),
    "setMinimum":             (1, 1, "setMinimum(value)"),
    "setValue":               (1, 1, "setValue(value)"),
    "setRange":               (2, 2, "setRange(minimum, maximum)"),
    "setAlignment":           (1, 1, "setAlignment(alignment)"),
    "setFont":                (1, 1, "setFont(font)"),
    "setStyleSheet":          (1, 1, "setStyleSheet(styleSheet)"),
    "setFixedSize":           (1, 2, "setFixedSize(width, height) or setFixedSize(QSize)"),
    "setFixedWidth":          (1, 1, "setFixedWidth(width)"),
    "setFixedHeight":         (1, 1, "setFixedHeight(height)"),
    "resize":                 (1, 2, "resize(width, height) or resize(QSize)"),
    "move":                   (1, 2, "move(x, y) or move(QPoint)"),
    "addItem":                (1, 3, "addItem(text[, icon[, userData]])"),
    "addItems":               (1, 1, "addItems(texts)"),
    "insertItem":             (2, 4, "insertItem(index, text[, icon[, userData]])"),
    "setCurrentIndex":        (1, 1, "setCurrentIndex(index)"),
    "setCurrentText":         (1, 1, "setCurrentText(text)"),
    "setPixmap":              (1, 1, "setPixmap(pixmap)"),
    "setScaledContents":      (1, 1, "setScaledContents(scaled)"),
    "setWordWrap":            (1, 1, "setWordWrap(on)"),
    "setColumnCount":         (1, 1, "setColumnCount(columns)"),
    "setRowCount":            (1, 1, "setRowCount(rows)"),
    "setHorizontalHeaderLabels": (1, 1, "setHorizontalHeaderLabels(labels)"),
    "setVerticalHeaderLabels":   (1, 1, "setVerticalHeaderLabels(labels)"),
}


def _make_safe_wrapper(method_name, original_method, min_args, max_args, signature):
    """
    Return a wrapper that validates the argument count before forwarding
    to the original Qt C++ method.  Raises TypeError (visible in Thonny
    with full traceback + line number) instead of crashing natively.
    """
    def _wrapper(self, *args, **kwargs):
        n = len(args) + len(kwargs)
        if n < min_args or n > max_args:
            expected = (
                f"exactly {min_args}" if min_args == max_args
                else f"{min_args} to {max_args}"
            )
            raise TypeError(
                f"{type(self).__name__}.{method_name}() takes {expected} "
                f"argument(s) but {n} {'was' if n == 1 else 'were'} given.\n"
                f"  Correct usage: {signature}"
            )
        return original_method(self, *args, **kwargs)

    _wrapper.__name__ = method_name
    _wrapper.__qualname__ = f"<pyqt5_safe>.{method_name}"
    return _wrapper


def _patch_qt_class(cls):
    """Patch a single Qt class in-place."""
    for method_name, (min_a, max_a, sig) in _QT_METHOD_SIGNATURES.items():
        original = getattr(cls, method_name, None)
        if original is None:
            continue
        # Don't double-wrap
        if getattr(original, "_pyqt5_safe_wrapped", False):
            continue
        wrapper = _make_safe_wrapper(method_name, original, min_a, max_a, sig)
        wrapper._pyqt5_safe_wrapped = True
        try:
            setattr(cls, method_name, wrapper)
        except (AttributeError, TypeError):
            pass  # Some sip-wrapped classes are read-only; leave them


def _patch_pyqt5_widgets(module):
    """Called once after PyQt5.QtWidgets is imported."""
    # The classes we care about most for beginners
    target_classes = [
        "QWidget", "QLabel", "QLineEdit", "QPushButton", "QTextEdit",
        "QPlainTextEdit", "QCheckBox", "QRadioButton", "QComboBox",
        "QSpinBox", "QDoubleSpinBox", "QSlider", "QDial",
        "QGroupBox", "QTabWidget", "QListWidget", "QTableWidget",
        "QTreeWidget", "QProgressBar", "QLCDNumber",
    ]
    for class_name in target_classes:
        cls = getattr(module, class_name, None)
        if cls is not None:
            _patch_qt_class(cls)


def load_plugin():
    from thonny.plugins.cpython_backend import get_backend
    backend = get_backend()
    backend.add_import_handler("PyQt5.QtWidgets", _patch_pyqt5_widgets)
