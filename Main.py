from PyQt5 import QtWidgets as pyqt
from PyQt5.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QPushButton, QMessageBox, QLabel, QScrollArea, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
from Camera import GrassBuddyCamera
from Auth import AuthWidget
from Leaderboard import GrassBuddyLeaderboard

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

        # Leaderboard Button
        self.leaderboard_btn = QPushButton("Leaderboard")
        self.leaderboard_btn.setFixedHeight(50)
        self.leaderboard_btn.clicked.connect(self.show_leaderboard)
        self.main_menu_layout.addWidget(self.leaderboard_btn)

        # Feed Label
        self.feed_label = QLabel("Recent Feed (Top 10):")
        self.main_menu_layout.addWidget(self.feed_label)

        # Scroll Area for Feed
        self.feed_scroll_area = QScrollArea()
        self.feed_scroll_area.setWidgetResizable(True)
        self.main_menu_layout.addWidget(self.feed_scroll_area)

        # Container inside Scroll Area
        self.feed_container = QWidget()
        self.feed_layout = QVBoxLayout(self.feed_container)
        self.feed_scroll_area.setWidget(self.feed_container)

        # Add Main Menu to stack
        self.stacked_widget.addWidget(self.main_menu_widget)

        # 3. Camera Widget (Index 2)
        self.camera_widget = GrassBuddyCamera()
        # Connect the camera's close signal to go back to main menu
        self.camera_widget.camera_closed.connect(self.show_main_menu)
        
        # Add Camera to stack
        self.stacked_widget.addWidget(self.camera_widget)

        # 4. Leaderboard Widget (Index 3)
        self.leaderboard_widget = GrassBuddyLeaderboard()
        self.leaderboard_widget.back_signal.connect(self.show_main_menu)
        self.stacked_widget.addWidget(self.leaderboard_widget)
        
        # Start at Login (Index 0)
        self.stacked_widget.setCurrentIndex(0)
        
        # User auth state (token, id, name)
        self.current_user = None

    def show_leaderboard(self):
        self.leaderboard_widget.refresh_leaderboard()
        self.stacked_widget.setCurrentIndex(3)

    def on_login_success(self, user_data):
        self.current_user = user_data
        QMessageBox.information(self, "Welcome", f"Welcome back, {user_data['name']}!")
        # Refresh Feed
        self.refresh_feed()
        # Switch to Main Menu
        self.stacked_widget.setCurrentIndex(1)

    def refresh_feed(self):
        # Clear existing layout
        while self.feed_layout.count():
            item = self.feed_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        try:
            # Assume backend is running on localhost:5000
            response = requests.get('http://10.2.0.2:5000/feed')
            if response.status_code == 200:
                data = response.json()
                feed_items = data.get('feed', [])
                print(feed_items)
                for item in feed_items:
                    # Create Feed Item Widget
                    item_widget = QWidget()
                    item_layout = QVBoxLayout(item_widget)
                    item_widget.setStyleSheet("border: 1px solid gray; margin: 5px;")
                    
                    # Username label
                    user_label = QLabel(f"User: {item['user']} - {item['timestamp']}")
                    user_label.setStyleSheet("font-weight: bold; border: none;")
                    item_layout.addWidget(user_label)
                    
                    # Image
                    img_label = QLabel()
                    img_label.setStyleSheet("border: none;")
                    image_url = f"http://10.2.0.2:5000{item['url']}"
                    
                    try:
                        img_data = requests.get(image_url).content
                        pixmap = QPixmap()
                        pixmap.loadFromData(img_data)
                        if not pixmap.isNull():
                            pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio)
                            img_label.setPixmap(pixmap)
                        else:
                            img_label.setText("Invalid Image")
                    except Exception as e:
                        img_label.setText("Failed to load image")
                        print(f"Error loading image: {e}")
                    
                    item_layout.addWidget(img_label)
                    self.feed_layout.addWidget(item_widget)
            else:
                error_label = QLabel("Failed to fetch feed.")
                self.feed_layout.addWidget(error_label)
        except Exception as e:
            error_label = QLabel(f"Error connecting to server: {e}")
            self.feed_layout.addWidget(error_label)

    def show_camera(self):
        # Update camera with current user token
        if self.current_user:
            self.camera_widget.user_token = self.current_user.get('token')
            
        # Start the camera when showing the widget
        if self.camera_widget.camera:
            if self.camera_widget.camera.state() != 2: # 2 is QCamera.ActiveState
                 self.camera_widget.camera.start()
            self.stacked_widget.setCurrentIndex(2)
        else:
            QMessageBox.critical(self, "Camera Error", "No camera available.")

    def show_main_menu(self):
        # Stop the camera when going back (optional, handled in Camera close_camera too)
        if self.camera_widget.camera:
            self.camera_widget.camera.stop()
        self.refresh_feed()
        self.stacked_widget.setCurrentIndex(1)

if __name__ == "__main__":
    app = pyqt.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()