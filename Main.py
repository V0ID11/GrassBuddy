from PyQt6 import QtWidgets as pyqt

class MainWindow(pyqt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Main Window")
        self.setGeometry(100, 100, 600, 400)



if __name__ == "__main__":
    app = pyqt.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()