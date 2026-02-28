from PyQt5 import QtWidgets as pyqt
from PyQt5.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QPushButton
from Camera import GrassBuddyCamera

class MainWindow(pyqt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GrassBuddy Main Window")
        self.setGeometry(100, 100, 600, 400)

        # QStackedWidget to hold multiple views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 1. Main Menu Widget
        self.main_menu_widget = QWidget()
        self.main_menu_layout = QVBoxLayout(self.main_menu_widget)
        
        # Camera Button on Main Menu
        self.camera_btn = QPushButton("Open Camera")
        self.camera_btn.setFixedHeight(50)
        self.camera_btn.clicked.connect(self.show_camera)
        self.main_menu_layout.addWidget(self.camera_btn)

        # Add Main Menu to stack (Index 0)
        self.stacked_widget.addWidget(self.main_menu_widget)

        # 2. Camera Widget
        self.camera_widget = GrassBuddyCamera()
        # Connect the camera's close signal to go back to main menu
        self.camera_widget.camera_closed.connect(self.show_main_menu)
        
        # Add Camera to stack (Index 1)
        self.stacked_widget.addWidget(self.camera_widget)

    def show_camera(self):
        # Start the camera when showing the widget
        self.camera_widget.camera.start()
        self.stacked_widget.setCurrentIndex(1)

    def show_main_menu(self):
        # Stop the camera when going back (optional, handled in Camera close_camera too)
        self.camera_widget.camera.stop()
        self.stacked_widget.setCurrentIndex(0)

if __name__ == "__main__":
    app = pyqt.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()