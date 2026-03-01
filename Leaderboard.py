import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QScrollArea, QFrame, QApplication)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
import requests

# Assuming server is local for now
SERVER_URL = os.getenv("GRASSAPI")

class LeaderboardItem(QFrame):
    def __init__(self, rank, name, score, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.setStyleSheet("""
            QFrame {
                background-color: #424242;
                border: 1px solid #505050;
                border-radius: 10px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Rank Label
        self.rank_label = QLabel(f"#{rank}")
        rank_font = QFont()
        rank_font.setPointSize(18)
        rank_font.setBold(True)
        self.rank_label.setFont(rank_font)
        # Gold for 1st, Silver for 2nd, Bronze for 3rd, White for others
        if rank == 1:
            color = "#FFD700" # Gold
        elif rank == 2:
            color = "#C0C0C0" # Silver
        elif rank == 3:
            color = "#CD7F32" # Bronze
        else:
            color = "#E0E0E0"
            
        self.rank_label.setStyleSheet(f"color: {color}; border: none; background: transparent;")
        self.rank_label.setFixedWidth(60)
        layout.addWidget(self.rank_label)

        # Name Label
        self.name_label = QLabel(name)
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        self.name_label.setStyleSheet("border: none; background: transparent; color: white;")
        layout.addWidget(self.name_label)
        
        layout.addStretch()
        
        # Score Label
        self.score_label = QLabel(f"{score} pts")
        score_font = QFont()
        score_font.setPointSize(16)
        score_font.setBold(True)
        self.score_label.setFont(score_font)
        self.score_label.setStyleSheet("color: #81C784; border: none; background: transparent;")
        layout.addWidget(self.score_label)

class GrassBuddyLeaderboard(QMainWindow):
    back_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        # Central Widget Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Area
        header_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("Back")
        self.back_btn.setFixedSize(120, 70)
        self.back_btn.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.back_btn.clicked.connect(self.back_signal.emit)
        header_layout.addWidget(self.back_btn)
        
        title_label = QLabel("Leaderboard")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #4CAF50; margin-left: 20px;")
        header_layout.addWidget(title_label)
        
        # Spacer
        spacer = QLabel()
        spacer.setFixedSize(120, 70)
        header_layout.addWidget(spacer)
        
        self.main_layout.addLayout(header_layout)
        
        # Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #555;")
        self.main_layout.addWidget(line)
        
        # Scroll Area for List
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: transparent;")
        
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background-color: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setAlignment(Qt.AlignTop)
        self.list_layout.setSpacing(10) # Space between items
        
        self.scroll_area.setWidget(self.list_container)
        self.main_layout.addWidget(self.scroll_area)
        
        # Refresh Button at Bottom
        self.refresh_btn = QPushButton("Refresh Leaderboard")
        self.refresh_btn.setFixedHeight(80)
        self.refresh_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.refresh_btn.clicked.connect(self.refresh_leaderboard)
        self.main_layout.addWidget(self.refresh_btn)

    def refresh_leaderboard(self):
        # Clear existing items
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Show loading indicator
        loading_label = QLabel("Loading Leaderboard...")
        loading_label.setAlignment(Qt.AlignCenter)
        loading_label.setStyleSheet("font-size: 18px; color: #aaa;")
        self.list_layout.addWidget(loading_label)
        QApplication.processEvents()

        try:
            url = f"{os.getenv('GRASSAPI')}/leaderboard"
            try:
                response = requests.get(url, timeout=3)
            except:
                # Fallback to localhost if env var fails or connection fails
                url = "http://127.0.0.1:5000/leaderboard"
                response = requests.get(url, timeout=3)

            if response.status_code == 200:
                data = response.json().get('leaderboard_data', [])
                
                # Remove loading label
                if self.list_layout.count() > 0:
                    child = self.list_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                
                if not data:
                    empty_label = QLabel("No entries found.")
                    empty_label.setAlignment(Qt.AlignCenter)
                    self.list_layout.addWidget(empty_label)
                    return
                
                # Sort by score descending just in case
                # data.sort(key=lambda x: x.get('score', 0), reverse=True)

                for i, entry in enumerate(data):
                    name = entry.get('name', 'Unknown')
                    score = entry.get('score', 0)
                    item = LeaderboardItem(i + 1, name, score)
                    self.list_layout.addWidget(item)
            else:
                 self.handle_error(f"Server Error: {response.status_code}")

        except Exception as e:
            self.handle_error(f"Connection Error: {str(e)}")

    def handle_error(self, message):
        # Clear loading
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        error_label = QLabel(message)
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("font-size: 16px; color: #FF5252;")
        self.list_layout.addWidget(error_label)
        print(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GrassBuddyLeaderboard()
    window.show()
    window.refresh_leaderboard()
    sys.exit(app.exec_())
