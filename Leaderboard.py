
from FlaskBackend import get_leaderboard_data
import sys
from PyQt5 import QtWidgets, uic
import requests

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        
        uic.loadUi('Leaderboard.ui', self)
        self.refresh_leaderboard()

        

    def handle_click(self):
        print("Button clicked!")
        self.status_label.setText("Processing...")
    def refresh_leaderboard(self):
            try:
                URL = "http://10.14.210.2:5000/leaderboard" 
                response = requests.get(URL)
                data = response.json().get('leaderboard_data', [])

                # Clear existing items in the layout (in case of a refresh)
                while self.verticalLayout.count():
                    child = self.verticalLayout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

                # Iterate through the dictionary and add widgets
                for entry in data:
                    self.add_leaderboard_row(entry['name'], entry['score'])

            except Exception as e:
                print(f"Error connecting to server: {e}")

    def add_leaderboard_row(self, name, score):
        row_item = QtWidgets.QWidget()
        uic.loadUi('leaderboardwidget.ui', row_item)
        

        row_item.name.setText(name)
        row_item.score.setText(str(score))
        
        self.verticalLayout.addWidget(row_item)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())