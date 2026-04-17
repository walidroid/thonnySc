import sys
import tempfile
import PyQt5.QtWidgets as qw
import PyQt5.uic as uic

def safe_excepthook(exc_type, exc_value, exc_traceback):
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

# Override the default hook
sys.excepthook = safe_excepthook

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

print("Testing uic loadUi setText with wrong args:")
label.setText('test', 123)

print("Did the app survive? Yes!")
