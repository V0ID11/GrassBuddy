import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox,QHBoxLayout
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtCore import Qt

class GrassBuddyCamera(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GrassBuddy Camera")
        self.setGeometry(100, 100, 800, 600)

        # Main layout container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Setup Camera
        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            QMessageBox.warning(self, "Error", "No camera content found.")
            sys.exit()

        self.current_camera_index = 0
        self.camera = QCamera(self.available_cameras[self.current_camera_index])

        # Viewfinder to see what the camera sees
        self.viewfinder = QCameraViewfinder()
        self.layout.addWidget(self.viewfinder)
        self.camera.setViewfinder(self.viewfinder)

        # Image Capture object
        self.image_capture = QCameraImageCapture(self.camera)
        self.image_capture.imageCaptured.connect(self.image_captured)
        self.image_capture.imageSaved.connect(self.image_saved)

        # Camera Controls Layout
        self.controls_layout = QHBoxLayout()
        self.layout.addLayout(self.controls_layout)

        # Switch Camera Button (only if multiple cameras exist)
        if len(self.available_cameras) > 1:
            self.switch_btn = QPushButton("Switch Camera")
            self.switch_btn.setFixedHeight(50)
            self.switch_btn.clicked.connect(self.switch_camera)
            self.controls_layout.addWidget(self.switch_btn)

        # Capture Button
        self.capture_btn = QPushButton("Touch Grass (Take Photo)")
        self.capture_btn.setFixedHeight(50)
        self.capture_btn.clicked.connect(self.capture_image)
        self.controls_layout.addWidget(self.capture_btn)

        # Start Camera
        self.camera.start()

    def switch_camera(self):
        self.camera.stop()
        self.current_camera_index = (self.current_camera_index + 1) % len(self.available_cameras)
        self.camera = QCamera(self.available_cameras[self.current_camera_index])
        self.camera.setViewfinder(self.viewfinder)
        
        # We need to recreate the image capture object for the new camera
        self.image_capture = QCameraImageCapture(self.camera)
        self.image_capture.imageCaptured.connect(self.image_captured)
        self.image_capture.imageSaved.connect(self.image_saved)
        
        self.camera.start()


    def capture_image(self):
        # Generate a timestamp for the filename
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        # Ensure the directory exists
        save_dir = os.path.join(os.getcwd(), "grass_photos")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        filename = os.path.join(save_dir, f"grass_{timestamp}.jpg")
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        self.image_capture.capture(filename)

    def image_captured(self, id, image):
        print(f"Image captured with ID: {id}")

    def image_saved(self, id, filename):
        print(f"Image saved to: {filename}")
        QMessageBox.information(self, "Success", f"Grass touched! Photo saved to:\n{filename}")
        self.close()

    def closeEvent(self, event):
        if self.camera.state() == QCamera.ActiveState:
            self.camera.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GrassBuddyCamera()
    window.show()
    sys.exit(app.exec_())