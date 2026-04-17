import PyQt5.QtWidgets as qw

app = qw.QApplication([])
label = qw.QLabel()

print("Trigger top level crash")
label.setText("test", 123)
print("WILL NOT REACH")
