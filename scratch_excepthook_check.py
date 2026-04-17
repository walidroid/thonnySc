import sys
import tempfile
print("AT START OF SCRIPT:", sys.excepthook)

def safe_excepthook(exc_type, exc_value, exc_traceback):
    print("CUSTOM EXCEPTHOOK WAS TRIGGERED!!!")
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = safe_excepthook

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

print("Testing uic loadUi setText with wrong args:")
try:
    # We do a click simulation instead to trigger the slot
    btn = qw.QPushButton("Click me")
    
    def my_slot():
        btn.setText('test', 123)
        
    btn.clicked.connect(my_slot)
    btn.click()
except Exception as e:
    print("Error caught normally:", e)

print("Did it survive?")
