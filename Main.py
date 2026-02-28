from PyQt5 import QtWidgets as pyqt
from PyQt5.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QPushButton, QMessageBox
from Camera import GrassBuddyCamera
from Auth import AuthWidget

class MainWindow(pyqt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GrassBuddy Main Window")
        self.setGeometry(100, 100, 600, 400)

        # QStackedWidget to hold multiple views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 1. Login/Auth View (Index 0)
        self.auth_widget = AuthWidget()
        self.auth_widget.login_success.connect(self.on_login_success)
        self.stacked_widget.addWidget(self.auth_widget)

        # 2. Main Menu Widget (Index 1)
        self.main_menu_widget = QWidget()
        self.main_menu_layout = QVBoxLayout(self.main_menu_widget)
        
        # Camera Button on Main Menu
        self.camera_btn = QPushButton("Open Camera")
        self.camera_btn.setFixedHeight(50)
        self.camera_btn.clicked.connect(self.show_camera)
        self.main_menu_layout.addWidget(self.camera_btn)

        # Add Main Menu to stack
        self.stacked_widget.addWidget(self.main_menu_widget)

        # 3. Camera Widget (Index 2)
        self.camera_widget = GrassBuddyCamera()
        # Connect the camera's close signal to go back to main menu
        self.camera_widget.camera_closed.connect(self.show_main_menu)
        
        # Add Camera to stack
        self.stacked_widget.addWidget(self.camera_widget)
        
        # Start at Login (Index 0)
        self.stacked_widget.setCurrentIndex(0)
        
        # User auth state (token, id, name)
        self.current_user = None

    def on_login_success(self, user_data):
        self.current_user = user_data
        QMessageBox.information(self, "Welcome", f"Welcome back, {user_data['name']}!")
        # Switch to Main Menu
        self.stacked_widget.setCurrentIndex(1)

    def show_camera(self):
        # Start the camera when showing the widget
        self.camera_widget.camera.start()
        self.stacked_widget.setCurrentIndex(2)

    def show_main_menu(self):
        # Stop the camera when going back (optional, handled in Camera close_camera too)
        self.camera_widget.camera.stop()
        self.stacked_widget.setCurrentIndex(1)

if __name__ == "__main__":
    app = pyqt.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()