from PyQt5.QtCore import QThread, pyqtSignal

import requests
import time
import os

api = os.getenv("GRASSAPI")
nudge_url = f"{api}/nudge"
listen_url = f"{api}/notifications"


class Nudger(QThread):
    """
    sends nudge events to api
    """
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(bool, str)

    def __init__(self, target_uid, auth_tok):
        super().__init__()
        self.target_uid = target_uid
        self.auth_tok = auth_tok

    def run(self):
        self.started.emit()
        headers = {"Authorization": f"Bearer {self.auth_tok}"}
        try:
            response = requests.post(f"{nudge_url}/{self.target_uid}",
                                     headers=headers,
                                     timeout=5)
            if response.status_code == 200:
                self.finished.emit(True, "Nudge sent!")
            else:
                self.error.emit(False, f"Error {response.status_code}")
        except Exception as e:
            self.error.emit(False, str(e))


class NudgeListener(QThread):
    """
    listens for the nudge
    """
    nudge_received = pyqtSignal(str)

    def __init__(self, auth_tok):
        super().__init__()
        self.auth_tok = auth_tok
        self._is_running = True

    def run(self):
        headers = {"Authorization": f"Bearer {self.auth_tok}"}
        while self._is_running:
            try:
                response = requests.get(listen_url,
                                        headers=headers,
                                        timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    #print(data)
                    for nudge in data.get("notifications"):
                        message = nudge['message']
                        self.nudge_received.emit(message)

            except Exception as e:
                print(f"Polling error: {e}")

            time.sleep(5)

    def stop(self):
        self._is_running = False
