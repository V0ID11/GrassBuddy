import sys
import networker
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget


class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nudge Test Environment")

        # UI Elements
        self.status_label = QLabel("Waiting for interaction...")
        self.btn = QPushButton("Send Test Nudge to Self")
        self.btn.clicked.connect(self.send_test_nudge)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.btn)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def send_test_nudge(self):
        self.status_label.setText("Sending...")
        self.nudger = networker.Nudger("1", "auth_sarah_2")
        self.nudger.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec())
