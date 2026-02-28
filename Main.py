from PyQt5 import QtWidgets as pyqt
from Camera import GrassBuddyCamera

class MainWindow(pyqt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GrassBuddy Main Window")
        self.setGeometry(100, 100, 600, 400)

        # Central widget and layout
        self.central_widget = pyqt.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = pyqt.QVBoxLayout(self.central_widget)

        # Camera Button
        self.camera_btn = pyqt.QPushButton("Open Camera")
        self.camera_btn.setFixedHeight(50)
        self.camera_btn.clicked.connect(self.open_camera)
        self.layout.addWidget(self.camera_btn)

    def open_camera(self):
        self.camera_window = GrassBuddyCamera(self)
        self.camera_window.show()

if __name__ == "__main__":
    app = pyqt.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()