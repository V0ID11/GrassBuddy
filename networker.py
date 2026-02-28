from PyQt5.QtCore import QThread, pyqtSignal

import websockets
import requests
import asyncio
import json


api = "http://10.14.210.2:5000"
nudge_url = f"{api}/nudge"
websock = ""


class Nudger(QThread):
    """
    sends nudge events to api
    """
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, target_uid, auth_tok):
        super().__init__()
        self.target_uid = target_uid
        self.auth_tok = auth_tok

    def run(self):
        self.started.emit()
        headers = {"Auth": f"Bearer {self.auth_tok}"}
        payload = {"recipient_id": self.target_uid}
        try:
            response = requests.post(nudge_url,
                                     json=payload,
                                     headers=headers,
                                     timeout=5)
            if response.status_code == 200:
                self.finished.emit(True, "Nudge sent!")
            else:
                self.error.emit(False, f"Error {response.status_code}")
        except Exception as e:
            self.error.emit(str(e))


class NudgeListener(QThread):
    """
    listens for the nudge
    """
    nudge_recieved = pyqtSignal(str)

    def __init__(self, user_tok):
        super().__init__()
        self.user_tok = user_tok
        self._is_running = True

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.listen())

    async def listen(self):
        uri = f"{websock}/notifications?token={self.user_tok}"

        try:
            async with websockets.connect(uri) as websocket:
                while self._is_running:
                    message = await websocket.recv()
                    data = json.loads(message)

                    if data.get("type") == "nudge":
                        sender = data.get("from_user", "someone")
                        self.nudge_received.emit(sender)
        except Exception as e:
            print(f"Connection error: {e}")

    def stop(self):
        self._is_running = False
        self.quit()
