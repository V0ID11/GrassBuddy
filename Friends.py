from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QListWidget, QListWidgetItem, 
                             QMessageBox, QTabWidget)
from PyQt5.QtCore import pyqtSignal, Qt
import requests
from networker import Nudger
import os

# Assuming server is local for now, can be configured
SERVER_URL = os.getenv("GRASSAPI")

class FriendItem(QWidget):
    def __init__(self, user_id, name, token, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.token = token
        
        # Increase bar size
        self.setMinimumHeight(70)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        self.label = QLabel(name)
        # Make name larger
        font = self.label.font()
        font.setPointSize(14) 
        self.label.setFont(font)
        layout.addWidget(self.label)
        
        self.nudge_btn = QPushButton("Nudge")
        # self.nudge_btn.setObjectName("secondary_btn") # Removed to make it primary (Green)
        self.nudge_btn.setFixedSize(120, 45) # Bigger button
        self.nudge_btn.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.nudge_btn.clicked.connect(self.send_nudge)
        layout.addWidget(self.nudge_btn)

    def send_nudge(self):
        self.nudge_btn.setEnabled(False)
        self.nudge_btn.setText("Nudging...")
        
        self.nudger = Nudger(self.user_id, self.token, SERVER_URL)
        self.nudger.finished.connect(self.on_nudge_success)
        self.nudger.error.connect(self.on_nudge_error)
        self.nudger.start()
        
    def on_nudge_success(self):
        self.nudge_btn.setText("Nudged!")
        self.nudge_btn.setEnabled(True)
        # Reset text after a delay if desired, but this is fine

    def on_nudge_error(self, success, msg):
        self.nudge_btn.setText("Retry")
        self.nudge_btn.setEnabled(True)
        print(f"Nudge failed: {msg}")

class FriendRequestItem(QWidget):
    def __init__(self, req_id, username, name, parent=None):
        super().__init__(parent)
        self.req_id = req_id
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.label = QLabel(f"{name} ({username})")
        layout.addWidget(self.label)
        
        self.accept_btn = QPushButton("Accept")
        self.accept_btn.setObjectName("primary_btn") # Uses default success color
        layout.addWidget(self.accept_btn)
        
        self.reject_btn = QPushButton("Reject")
        self.reject_btn.setObjectName("danger_btn")
        layout.addWidget(self.reject_btn)

class FriendsWidget(QWidget):
    back_signal = pyqtSignal()

    def __init__(self, user_token=None):
        super().__init__()
        self.user_token = user_token
        self.user_id = None

        
        layout = QVBoxLayout(self)
        
        # Header with Back Button
        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("Back")
        self.back_btn.clicked.connect(self.back_signal.emit)
        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Tab 1: My Friends
        self.friends_tab = QWidget()
        self.friends_layout = QVBoxLayout(self.friends_tab)
        self.friends_list = QListWidget()
        self.friends_layout.addWidget(self.friends_list)
        self.refresh_friends_btn = QPushButton("Refresh Friends")
        self.refresh_friends_btn.clicked.connect(self.load_friends)
        self.friends_layout.addWidget(self.refresh_friends_btn)
        self.tabs.addTab(self.friends_tab, "My Friends")
        
        # Tab 2: Pending Requests
        self.requests_tab = QWidget()
        self.requests_layout = QVBoxLayout(self.requests_tab)
        self.requests_list = QListWidget()
        self.requests_layout.addWidget(self.requests_list)
        self.refresh_requests_btn = QPushButton("Refresh Requests")
        self.refresh_requests_btn.clicked.connect(self.load_requests)
        self.requests_layout.addWidget(self.refresh_requests_btn)
        self.tabs.addTab(self.requests_tab, "Requests")
        
        # Tab 3: Add Friend
        self.add_tab = QWidget()
        self.add_layout = QVBoxLayout(self.add_tab)
        
        self.add_input = QLineEdit()
        self.add_input.setPlaceholderText("Enter username to add...")
        self.add_layout.addWidget(self.add_input)
        
        self.send_req_btn = QPushButton("Send Friend Request")
        self.send_req_btn.clicked.connect(self.send_request)
        self.add_layout.addWidget(self.send_req_btn)
        self.add_layout.addStretch()
        
        self.tabs.addTab(self.add_tab, "Add Friend")

    def set_token(self, token, user_id):
        self.user_token = token
        self.user_id = user_id
        self.load_friends()
        self.load_requests()

    def load_friends(self):
        if not self.user_token: return
        self.friends_list.clear()
        
        try:
            # Note: Using localhost/IP fallback
            url = f"{SERVER_URL}/users/{self.user_id}/friends"
            try:
                response = requests.get(url, timeout=2)
            except:
                url = f"http://127.0.0.1:5000/users/{self.user_id}/friends"
                response = requests.get(url)
                
            if response.status_code == 200:
                friends = response.json().get('friends', [])
                for f in friends:
                    item = QListWidgetItem(self.friends_list)
                    widget = FriendItem(f['id'], f['name'], self.user_token)
                    item.setSizeHint(widget.sizeHint())
                    self.friends_list.setItemWidget(item, widget)
            else:
                self.friends_list.addItem("Failed to load friends.")
        except Exception as e:
            print(f"Error loading friends: {e}")

    def on_nudge_success(self, success, msg):
        QMessageBox.information(self, "Success", msg)

    def on_nudge_error(self, success, msg):
        QMessageBox.warning(self, "Error", msg)

    def load_requests(self):
        if not self.user_token: return
        self.requests_list.clear()
        
        headers = {'Authorization': f'Bearer {self.user_token}'}
        try:
            url = f"{SERVER_URL}/friend_request/list"
            try:
                response = requests.get(url, headers=headers, timeout=2)
            except:
                url = f"http://127.0.0.1:5000/friend_request/list"
                response = requests.get(url, headers=headers)
                
            if response.status_code == 200:
                reqs = response.json().get('requests', [])
                for r in reqs:
                    item = QListWidgetItem(self.requests_list)
                    widget = FriendRequestItem(r['req_id'], r['username'], r['name'])
                    widget.accept_btn.clicked.connect(lambda ch, rid=r['req_id']: self.respond_request(rid, 'accept'))
                    widget.reject_btn.clicked.connect(lambda ch, rid=r['req_id']: self.respond_request(rid, 'reject'))
                    
                    item.setSizeHint(widget.sizeHint())
                    self.requests_list.setItemWidget(item, widget)
                
                if not reqs:
                    self.requests_list.addItem("No pending requests.")
            else:
                print(response.text)
        except Exception as e:
            print(f"Error loading requests: {e}")

    def respond_request(self, req_id, action):
        headers = {'Authorization': f'Bearer {self.user_token}'}
        try:
            url = f"{SERVER_URL}/friend_request/respond"
            try:
                response = requests.post(url, json={'req_id': req_id, 'action': action}, headers=headers, timeout=2)
            except:
                url = f"http://127.0.0.1:5000/friend_request/respond"
                response = requests.post(url, json={'req_id': req_id, 'action': action}, headers=headers)
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", f"Request {action}ed!")
                self.load_requests()
                self.load_friends()
            else:
                QMessageBox.warning(self, "Error", f"Failed: {response.json().get('error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {e}")

    def send_request(self):
        username = self.add_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Input Error", "Please enter a username.")
            return
            
        headers = {'Authorization': f'Bearer {self.user_token}'}
        try:
            url = f"{SERVER_URL}/friend_request/send"
            try:
                 response = requests.post(url, json={'username': username}, headers=headers, timeout=2)
            except:
                 url = f"http://127.0.0.1:5000/friend_request/send"
                 response = requests.post(url, json={'username': username}, headers=headers)

            if response.status_code == 201:
                QMessageBox.information(self, "Success", f"Friend request sent to {username}!")
                self.add_input.clear()
            else:
                err = response.json().get('error', 'Unknown error')
                QMessageBox.warning(self, "Error", f"Failed: {err}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {e}")
