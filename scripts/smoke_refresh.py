from ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
win = MainWindow()
# Call refresh once to ensure no runtime exception in the method
win.refresh()
print('refresh called ok')
