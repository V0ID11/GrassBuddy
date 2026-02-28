import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtCore import Qt, pyqtSignal

class GrassBuddyCamera(QWidget):
    camera_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)

        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            QMessageBox.warning(self, "Error", "No camera content found.")
            sys.exit()

        self.current_camera_index = 0
        self.camera = QCamera(self.available_cameras[self.current_camera_index])


        self.viewfinder = QCameraViewfinder()
        self.layout.addWidget(self.viewfinder)
        self.camera.setViewfinder(self.viewfinder)


        self.image_capture = QCameraImageCapture(self.camera)
        self.image_capture.imageCaptured.connect(self.image_captured)
        self.image_capture.imageSaved.connect(self.image_saved)


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


        self.capture_btn = QPushButton("Touch Grass (Take Photo)")
        self.capture_btn.setFixedHeight(50)
        self.capture_btn.clicked.connect(self.capture_image)
        self.controls_layout.addWidget(self.capture_btn)



    def close_camera(self):
        self.camera.stop()
        self.camera_closed.emit()


    def switch_camera(self):
        self.camera.stop()
        self.current_camera_index = (self.current_camera_index + 1) % len(self.available_cameras)
        self.camera = QCamera(self.available_cameras[self.current_camera_index])
        self.camera.setViewfinder(self.viewfinder)
        

        self.image_capture = QCameraImageCapture(self.camera)
        self.image_capture.imageCaptured.connect(self.image_captured)
        self.image_capture.imageSaved.connect(self.image_saved)
        
        self.camera.start()


    def capture_image(self):

        timestamp = time.strftime("%Y%m%d-%H%M%S")

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
        self.close_camera()

    def closeEvent(self, event):
        if self.camera.state() == QCamera.ActiveState:
            self.camera.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GrassBuddyCamera()

    window.camera.start()
    window.show()
    sys.exit(app.exec_())