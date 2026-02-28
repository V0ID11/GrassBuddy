import sys
import os
import time
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout, QCheckBox
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraImageCapture, QCameraViewfinderSettings
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtCore import Qt, pyqtSignal, QSize

# SERVER_URL should match your Flask server
SERVER_URL = os.getenv("GRASSAPI")

class GrassBuddyCamera(QWidget):
    camera_closed = pyqtSignal()

    def __init__(self, parent=None, user_token=None):
        super().__init__(parent)
        self.user_token = user_token
        
        self.layout = QVBoxLayout(self)

        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            # Don't exit the whole app, just disable camera features
            QMessageBox.warning(self, "Error", "No camera found. Camera features will be disabled.")
            self.camera = None
            return

        print(f"Found {len(self.available_cameras)} cameras:")
        for cam in self.available_cameras:
            print(f"- {cam.description()}")

        self.current_camera_index = 0
        try:
            self.camera = QCamera(self.available_cameras[self.current_camera_index])
            
            # Use explicit viewfinder settings to prevent negotiation failures
            # This often fixes the 0x800703e3 error on generic USB2.0 cameras
            viewfinder_settings = QCameraViewfinderSettings()
            viewfinder_settings.setResolution(QSize(640, 480))
            self.camera.setViewfinderSettings(viewfinder_settings)
            
            self.camera.setCaptureMode(QCamera.CaptureStillImage)
            print(f"Initialized camera: {self.available_cameras[self.current_camera_index].description()}")
        except Exception as e:
             QMessageBox.critical(self, "Camera Init Error", f"Failed to initialize camera: {e}")
             self.camera = None
             return

        self.viewfinder = QCameraViewfinder()
        self.layout.addWidget(self.viewfinder)
        self.camera.setViewfinder(self.viewfinder)
        
        # Load the camera to reserve resources before starting
        self.camera.load()
        
        # Connect error signal
        self.camera.error.connect(self.camera_error)

        self.image_capture = QCameraImageCapture(self.camera)
        self.image_capture.imageCaptured.connect(self.image_captured)
        self.image_capture.imageSaved.connect(self.image_saved)
        self.image_capture.error.connect(self.capture_error)

        self.controls_layout = QHBoxLayout()
        self.layout.addLayout(self.controls_layout)


        self.back_btn = QPushButton("Back")
        self.back_btn.setFixedHeight(50)
        self.back_btn.clicked.connect(self.close_camera)
        self.controls_layout.addWidget(self.back_btn)


        if len(self.available_cameras) > 1:
            self.switch_btn = QPushButton("Switch Camera")
            self.switch_btn.setFixedHeight(50)
            self.switch_btn.clicked.connect(self.switch_camera)
            self.controls_layout.addWidget(self.switch_btn)

        # Notify Friends Checkbox
        self.notify_friends_chk = QCheckBox("Nudge Friends")
        self.notify_friends_chk.setChecked(True)
        self.controls_layout.addWidget(self.notify_friends_chk)

        self.capture_btn = QPushButton("Touch Grass (Take Photo)")
        self.capture_btn.setFixedHeight(50)
        self.capture_btn.clicked.connect(self.capture_image)
        self.controls_layout.addWidget(self.capture_btn)



    def close_camera(self):
        if self.camera:
            self.camera.stop()
            self.camera.unload()
        self.camera_closed.emit()


    def switch_camera(self):
        if self.camera:
            self.camera.stop()
        self.current_camera_index = (self.current_camera_index + 1) % len(self.available_cameras)
        self.camera = QCamera(self.available_cameras[self.current_camera_index])
        self.camera.setViewfinder(self.viewfinder)
        
        # Reconnect error signal
        self.camera.error.connect(self.camera_error)
        self.camera.setCaptureMode(QCamera.CaptureStillImage)

        self.image_capture = QCameraImageCapture(self.camera)
        self.image_capture.imageCaptured.connect(self.image_captured)
        self.image_capture.imageSaved.connect(self.image_saved)
        self.image_capture.error.connect(self.capture_error)
        
        self.camera.start()


    def capture_image(self):
        # Generate a timestamp for the filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        # Ensure the directory exists
        save_dir = os.path.join(os.getcwd(), "grass_photos")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        filename = os.path.join(save_dir, f"grass_{timestamp}.jpg")
        
        # Ensure camera is ready
        if self.camera:
            if self.camera.state() != QCamera.ActiveState:
                self.camera.start()
                # Give it a moment to initialize
                QApplication.processEvents()
                time.sleep(0.1)
                
            if self.camera.status() != QCamera.ActiveStatus:
                print(f"Camera status not active: {self.camera.status()}")

        # Ensure camera is locked for focus/settings before capture
        # self.camera.searchAndLock() # Disabling lock as it causes issues on some cameras
        
        # Capture
        print("Attempting capture...")
        if self.image_capture.isReadyForCapture():
            self.image_capture.capture(filename)
        else:
            print("Image capture not ready.")
            QMessageBox.warning(self, "Camera Warning", "Camera is not ready for capture yet.")
        
        # Unlock
        # self.camera.unlock()

    def camera_error(self, error):
        error_msg = self.camera.errorString()
        print(f"Camera Error Code: {error} - {error_msg}")
        # Only show critical if it's not a recoverable error
        if error != QCamera.NoError:
             QMessageBox.critical(self, "Camera Error", f"Code: {error}\n{error_msg}")

    def capture_error(self, id, error, error_string):
        print(f"Capture Error ID {id}: {error} - {error_string}")
        # Sometimes permissions issues or invalid paths trigger this
        QMessageBox.warning(self, "Capture Error", f"Failed to capture image: {error_string}")

    def image_captured(self, id, image):
        print(f"Image captured with ID: {id}")

    def image_saved(self, id, filename):
        print(f"Local save: {filename}")
        
        server_msg = "Not logged in (local only)."
        score_msg = ""
        
        if self.user_token:
            try:
                # Prepare headers
                headers = {'Authorization': f'Bearer {self.user_token}'}
                data = {'notify_friends': 'true' if self.notify_friends_chk.isChecked() else 'false'}
                
                # Prepare file
                with open(filename, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(f"{SERVER_URL}/upload", files=files, data=data, headers=headers)
                
                if response.status_code == 201:
                    data = response.json()
                    score = data.get('score_added', 0)
                    server_msg = "Uploaded to server!"
                    score_msg = f"\nScore: +{score}"
                else:
                    server_msg = f"Upload failed: {response.status_code}"
                    print(response.text)
            except Exception as e:
                server_msg = f"Error: {str(e)}"
                print(e)

        QMessageBox.information(self, "Touch Grass", 
                              f"Photo saved locally.\n{server_msg}{score_msg}")
        self.close_camera()

    def closeEvent(self, event):
        if self.camera:
            self.camera.stop()
            self.camera.unload()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GrassBuddyCamera()
    
    if window.camera:
        window.camera.start()
        
    window.show()
    sys.exit(app.exec_())
