import sys
import PyQt5.QtWidgets as qw

def safe_excepthook(exc_type, exc_value, exc_traceback):
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = safe_excepthook

app = qw.QApplication([])
btn = qw.QPushButton("Click me")

def my_slot():
    btn.setText("test", 123)

btn.clicked.connect(my_slot)
print("Simulating click...")
btn.click()
print("Did it survive?")
