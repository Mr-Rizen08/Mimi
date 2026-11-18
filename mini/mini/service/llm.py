import json, requests
import traceback

from PySide6.QtCore import QThread, Signal


class ChatWorker(QThread):
    token = Signal(str)
    finished_ok = Signal()
    failed = Signal(str)

    def __init__(self, message, model: str = "qwen3.5:9b", url: str ="http://localhost:11434"):
        super().__init__()
        self.message , self.model, self.url = message, model, url

    def run(self):
        try:
            payload = {"model": self.model, "messages": self.message,
                       "stream": True, "think": False}
            print(payload)
            with requests.post(f"{self.url}/api/chat", json=payload, stream=True, timeout=120) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line: continue
                    chunk = json.loads(line)
                    text = chunk.get("message", {}).get("content", "")
                    print("EMIT:", repr(text))
                    self.token.emit(text)
                    print("RAW:", chunk)
                    if chunk.get("done"): break
            self.finished_ok.emit()
        except Exception as e:
            traceback.print_exc()
            self.failed.emit(str(e))


