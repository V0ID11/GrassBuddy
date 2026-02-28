import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtCore import Qt

class GrassBuddyCamera(QMainWindow):
    def __init__(self):
        super().__init__()
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

        # Use the default camera (usually the back camera on mobile or webcam on PC)
        self.camera = QCamera(self.available_cameras[0])

        # Viewfinder to see what the camera sees
        self.viewfinder = QCameraViewfinder()
        self.layout.addWidget(self.viewfinder)
        self.camera.setViewfinder(self.viewfinder)

        # Image Capture object
        self.image_capture = QCameraImageCapture(self.camera)
        self.image_capture.imageCaptured.connect(self.image_captured)
        self.image_capture.imageSaved.connect(self.image_saved)

        # Capture Button
        self.capture_btn = QPushButton("Touch Grass (Take Photo)")
        self.capture_btn.setFixedHeight(50)
        self.capture_btn.clicked.connect(self.capture_image)
        self.layout.addWidget(self.capture_btn)

        # Start Camera
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

    def closeEvent(self, event):
        if self.camera.state() == QCamera.ActiveState:
            self.camera.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GrassBuddyCamera()
    window.show()
    sys.exit(app.exec_())