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

print("Testing with 1 extra arg (number):")
try:
    label.setText('test', 123)
except Exception as e:
    print(type(e), e)

print("\nTesting with object arg:")
try:
    label.setText('test', object())
except Exception as e:
    print(type(e), e)
