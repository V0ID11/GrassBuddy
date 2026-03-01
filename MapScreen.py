from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap 
from PyQt5.QtCore import Qt, pyqtSignal
from LocationManager import LocationManager
import os

class MapScreen(QWidget):
    back_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.location_manager = LocationManager()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        
        # Header Area
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("Back")
        self.back_btn.setFixedSize(120, 70)
        self.back_btn.clicked.connect(self.back_signal.emit)
        header_layout.addWidget(self.back_btn)
        
        self.title_label = QLabel("Nearby Park")
        self.title_label.setObjectName("header_label")
        self.title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.title_label)
        
        # Spacer for balance
        spacer = QLabel()
        spacer.setFixedSize(120, 70)
        header_layout.addWidget(spacer)
        
        self.layout.addLayout(header_layout)

        # Park Name
        self.park_name_label = QLabel("Click 'Find Park' to start")
        self.park_name_label.setObjectName("sub_header")
        self.park_name_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.park_name_label)

        # Map Image Area
        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignCenter)
        self.map_label.setStyleSheet("border: 2px solid #555;")
        self.map_label.setMinimumSize(800, 500)
        self.layout.addWidget(self.map_label)
        
        # Action Button
        self.find_btn = QPushButton("Find Nearby Park")
        self.find_btn.setFixedHeight(80)
        self.find_btn.clicked.connect(self.load_map_data)
        self.layout.addWidget(self.find_btn)
        
        self.layout.addStretch()

    def load_map_data(self):
        self.park_name_label.setText("Updating location...")
        self.find_btn.setEnabled(False)
        self.find_btn.setText("Loading...")
        
        # Force UI update
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

        try:
            # 1. Update User Location
            self.location_manager.set_user_location()
            
            # 2. Find Nearby Park
            self.park_name_label.setText("Searching for parks...")
            QApplication.processEvents()
            self.location_manager.set_grass_location()
            
            # 3. Generate Route Map
            self.park_name_label.setText("Generating route...")
            QApplication.processEvents()
            
            success = self.location_manager.route_to_grass()
            
            if success:
                # Update Text
                park_name = self.location_manager.get_grass_location().get_name()
                self.park_name_label.setText(f"Go touch grass at: {park_name}")
                
                # Update Image
                if os.path.exists("route_map.png"):
                    pixmap = QPixmap("route_map.png")
                    scaled_pixmap = pixmap.scaled(self.map_label.width(), self.map_label.height(), 
                                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.map_label.setPixmap(scaled_pixmap)
                else:
                    self.map_label.setText("Map image saved but not found?")
            else:
                self.park_name_label.setText("Failed to generate route.")

        except Exception as e:
            self.park_name_label.setText("Error occurred")
            print(f"Map Error: {e}")
        
        self.find_btn.setEnabled(True)
        self.find_btn.setText("Find Nearby Park")
