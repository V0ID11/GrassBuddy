import os
from FlaskBackend import get_leaderboard_data
import sys
from PyQt5 import QtWidgets, uic, QtCore
import requests

class GrassBuddyLeaderboard(QtWidgets.QMainWindow):
    back_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(GrassBuddyLeaderboard, self).__init__()
        
        try:
            uic.loadUi('Leaderboard.ui', self)
        except Exception as e:
            print(f"Error loading UI: {e}")
            # Fallback if UI fails
            central_widget = QtWidgets.QWidget()
            self.setCentralWidget(central_widget)
            self.verticalLayout = QtWidgets.QVBoxLayout(central_widget)

        # Add Back Button
        self.back_btn = QtWidgets.QPushButton("Back to Menu")
        self.back_btn.clicked.connect(self.emit_back)
        # Assuming there is a layout we can add to, or we add to a toolbar/layout
        # Since we don't know the exact structure of Leaderboard.ui, let's try to find a layout or add a dock
        # Or simple: just add it to the top of verticalLayout if it exists
        if hasattr(self, 'verticalLayout'):
             self.verticalLayout.insertWidget(0, self.back_btn)
        else:
             # If no verticalLayout found from UI, we might be in trouble, but let's assume it works as previous code used it
             pass

        # self.refresh_leaderboard() # Call this when showing instead

    def emit_back(self):
        self.back_signal.emit()

    def handle_click(self):
        print("Button clicked!")
        if hasattr(self, 'status_label'):
            self.status_label.setText("Processing...")

    def refresh_leaderboard(self):
            try:
                # Use localhost for testing if needed, or keeping the IP
                URL = f"{os.getenv('GRASSAPI')}/leaderboard"
                try:
                    response = requests.get(URL, timeout=2)
                except:
                    # Fallback to localhost if IP fails
                    URL = "http://127.0.0.1:5000/leaderboard"
                    response = requests.get(URL)

                data = response.json().get('leaderboard_data', [])

                # Clear existing items in the layout (in case of a refresh)
                if hasattr(self, 'verticalLayout'):
                    # Keep the back button (index 0)
                    while self.verticalLayout.count() > 1:
                        child = self.verticalLayout.takeAt(1)
                        if child.widget():
                            child.widget().deleteLater()

                    # Iterate through the dictionary and add widgets
                    for entry in data:
                        self.add_leaderboard_row(entry['name'], entry['score'])
            except Exception as e:
                print(f"Error connecting to server: {e}")

    def add_leaderboard_row(self, name, score):
        if not hasattr(self, 'verticalLayout'): return

        row_item = QtWidgets.QWidget()
        try:
            uic.loadUi('leaderboardwidget.ui', row_item)
            row_item.name.setText(name)
            row_item.score.setText(str(score))
            self.verticalLayout.addWidget(row_item)
        except Exception as e:
            print(f"Error loading row UI: {e}")
            # Fallback row
            lbl = QtWidgets.QLabel(f"{name}: {score}")
            self.verticalLayout.addWidget(lbl)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GrassBuddyLeaderboard()
    window.refresh_leaderboard()
    window.show()
    window.show()
    sys.exit(app.exec_())
