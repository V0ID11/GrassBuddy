from PyQt5.QtCore import QThread, pyqtSignal

import requests
import time
import os

# Default, but can be overridden
DEFAULT_API = "http://10.2.0.2:5000" 

class Nudger(QThread):
    """
    sends nudge events to api
    """
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(bool, str)

    def __init__(self, target_uid, auth_tok, api_url=None):
        super().__init__()
        self.target_uid = target_uid
        self.auth_tok = auth_tok
        self.api_url = api_url or os.getenv("GRASSAPI") or DEFAULT_API

    def run(self):
        self.started.emit()
        nudge_url = f"{self.api_url}/nudge"
        headers = {"Authorization": f"Bearer {self.auth_tok}"}
        try:
            # Try primary URL
            response = requests.post(f"{nudge_url}/{self.target_uid}",
                                     headers=headers,
                                     timeout=5)
            if response.status_code == 200:
                self.finished.emit(True, "Nudge sent!")
            else:
                self.error.emit(False, f"Error {response.status_code}")
        except Exception:
             # Fallback to localhost if needed (simple retry logic)
             try:
                 fallback_url = "http://127.0.0.1:5000/nudge"
                 response = requests.post(f"{fallback_url}/{self.target_uid}",
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

    def __init__(self, auth_tok, api_url=None):
        super().__init__()
        self.auth_tok = auth_tok
        self.api_url = api_url or os.getenv("GRASSAPI") or DEFAULT_API
        self._is_running = True

    def run(self):
        listen_url = f"{self.api_url}/notifications"
        fallback_url = "http://127.0.0.1:5000/notifications"
        headers = {"Authorization": f"Bearer {self.auth_tok}"}
        
        while self._is_running:
            try:
                try:
                    response = requests.get(listen_url, headers=headers, timeout=5)
                except:
                    response = requests.get(fallback_url, headers=headers, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    for nudge in data.get("notifications", []):
                        message = nudge['message']
                        self.nudge_received.emit(message)

            except Exception as e:
                print(f"Polling error: {e}")

            time.sleep(5)

    def stop(self):
        self._is_running = False
