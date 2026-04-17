import sys
import PyQt5.QtWidgets as qw

def my_hook(type, value, tback):
    print("Caught in my_hook!", type)

sys.excepthook = my_hook

app = qw.QApplication([])
btn = qw.QPushButton("Click me")

def my_slot():
    btn.setText("test", 123)

btn.clicked.connect(my_slot)
print("Simulating click...")
btn.click()
print("Did it survive?")
