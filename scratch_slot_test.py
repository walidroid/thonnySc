import PyQt5.QtWidgets as qw

app = qw.QApplication([])
btn = qw.QPushButton("Click me")

def my_slot():
    btn.setText("test", 123)  # This will raise TypeError

btn.clicked.connect(my_slot)

print("Simulating click...")
btn.click()
print("Did it survive?")
