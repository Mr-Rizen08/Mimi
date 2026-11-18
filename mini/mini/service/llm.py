import json, requests
from PySide6.QtCore import QThread, Signal


class ChatWorker(QThread):
    token = Signal(str)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, message, model: str = "qwen3.5:9b", url: str ="http://localhost:11434"):
        super().__init__()
        self.message , self.model, self.url = message, model, url,

    def run(self):
        try:
            payload = {"model": self.model, "message": self.message,
                       "stream": True, "think": False}
            with requests.post(f"{self.url}/api/chat", json=payload) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line: continue
                    chunk = json.loads(line)
                    self.token.emit(chunk["message", {}]).get("content", "")
                    if chunk.get("done"): break
            self.finished_ok.emit()
        except Exception as e:
            self.failed.emit(str(e))