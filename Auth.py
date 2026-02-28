import os
import requests
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QHBoxLayout, QFrame)
from PyQt5.QtCore import pyqtSignal, Qt

# Change this to your server IP if running on a different machine
SERVER_URL = os.getenv("GRASSAPI")

class AuthWidget(QWidget):
    # Signals to communicate with the main window
    login_success = pyqtSignal(dict)  # Emits user data (token, id, name)
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Container to swap between Login and Signup
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.layout.addWidget(self.container)
        
        # Initialize with Login screen
        self.show_login()

    def show_login(self):
        self.clear_layout(self.container_layout)
        
        # Header
        header = QLabel("Login to GrassBuddy")
        header.setObjectName("header_label")
        header.setAlignment(Qt.AlignCenter)
        self.container_layout.addWidget(header)
        
        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.container_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.container_layout.addWidget(self.password_input)
        
        # Login Button
        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(40)
        login_btn.clicked.connect(self.handle_login)
        self.container_layout.addWidget(login_btn)
        
        # Switch to Register
        switch_layout = QHBoxLayout()
        switch_label = QLabel("Don't have an account?")
        switch_btn = QPushButton("Sign Up")
        switch_btn.setFlat(True)
        switch_btn.setStyleSheet("color: blue; text-decoration: underline;")
        switch_btn.setCursor(Qt.PointingHandCursor)
        switch_btn.clicked.connect(self.show_signup)
        
        switch_layout.addWidget(switch_label)
        switch_layout.addWidget(switch_btn)
        switch_layout.addStretch()
        self.container_layout.addLayout(switch_layout)
        
        self.container_layout.addStretch()

    def show_signup(self):
        self.clear_layout(self.container_layout)
        
        # Header
        header = QLabel("Create Account")
        header.setObjectName("header_label")
        header.setAlignment(Qt.AlignCenter)
        self.container_layout.addWidget(header)
        
        # Inputs
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Display Name (e.g. Nick)")
        self.container_layout.addWidget(self.name_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.container_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.container_layout.addWidget(self.password_input)
        
        # Register Button
        register_btn = QPushButton("Sign Up")
        register_btn.setFixedHeight(40)
        register_btn.clicked.connect(self.handle_register)
        self.container_layout.addWidget(register_btn)
        
        # Switch to Login
        switch_layout = QHBoxLayout()
        switch_label = QLabel("Already have an account?")
        switch_btn = QPushButton("Login")
        switch_btn.setFlat(True)
        switch_btn.setStyleSheet("color: blue; text-decoration: underline;")
        switch_btn.setCursor(Qt.PointingHandCursor)
        switch_btn.clicked.connect(self.show_login)
        
        switch_layout.addWidget(switch_label)
        switch_layout.addWidget(switch_btn)
        switch_layout.addStretch()
        self.container_layout.addLayout(switch_layout)
        
        self.container_layout.addStretch()

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
            
        try:
            response = requests.post(f"{SERVER_URL}/login", json={
                "username": username,
                "password": password
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                # Emit success signal with user data
                self.login_success.emit(data)
            else:
                error_msg = response.json().get('error', 'Login failed')
                QMessageBox.warning(self, "Login Error", error_msg)
                
        except requests.exceptions.ConnectionError as e:
            QMessageBox.critical(self, "Connection Error", "Could not connect to server. Is it running?")
            print(e)

    def handle_register(self):
        name = self.name_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not name or not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
            
        try:
            response = requests.post(f"{SERVER_URL}/register", json={
                "name": name,
                "username": username,
                "password": password
            }, timeout=5)
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Account created! Please login.")
                self.show_login()
            else:
                try:
                    error_msg = response.json().get('error', 'Registration failed')
                except ValueError:
                    # If response is not JSON (e.g. 500 server error HTML page)
                    error_msg = f"Server Error: {response.status_code}"
                    print(response.text) # Print to console for debugging
                    
                QMessageBox.warning(self, "Registration Error", error_msg)
                
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Connection Error", "Could not connect to server. Is it running?")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
