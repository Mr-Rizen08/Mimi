import re
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from mini.service.llm import ChatWorker

TAG = re.compile(r"^\s*\[(walk|idle|think|play)\]\s*")
SYSTEM = ("Ты — Мimi, дружелюбный питомец на рабочем столе. Отвечай по-русски, 1–3 предложения. "
          "В начале ответа можешь поставить один тег действия: [walk] [idle] [think] [play].")

class ChatWindow(QWidget):
    thinking = Signal()
    action = Signal(str)
    answered = Signal()

    def __init__(self, model="qwen3.5:9b"):
        super().__init__()
        self.setWindowTitle("Mini")
        self.resize(360, 420)
        self.model = model
        self.history, self.text, self.buf = [], "", ""
        self.acted = self.busy = False
        self.worker = None

        self.log = QTextEdit(); self.log.setReadOnly(True)
        self.input = QLineEdit(); self.input.setPlaceholderText("Скажи что-нибудь…")
        self.input.returnPressed.connect(self.send)
        lay = QVBoxLayout(self); lay.addWidget(self.log); lay.addWidget(self.input)

    def toggle(self):
        self.hide() if self.isVisible() else self.show()

    def send(self):
        q = self.input.text().strip()
        if not q or self.busy: return                  # пусто или прошлый запрос ещё идёт
        self.input.clear()
        self.history.append({"role": "user", "content": q})
        self.text += f"Ты: {q}\n"
        self.buf, self.acted, self.busy = "", False, True
        self.render("")
        msgs = [{"role": "system", "content": SYSTEM}, *self.history[-10:]]
        self.worker = ChatWorker(msgs, self.model)     # self.: иначе поток удалится
        self.worker.token.connect(self.on_token)
        self.worker.finished_ok.connect(self.on_done)
        self.worker.failed.connect(self.on_fail)
        self.worker.start()
        self.thinking.emit()

    def on_token(self, t):
        self.buf += t
        m = TAG.match(self.buf)
        if m and not self.acted:
            self.acted = True
            self.action.emit(m.group(1))
        self.render(TAG.sub("", self.buf))
    def on_done(self):
        self.history.append({"role": "assistant", "content": self.buf})
        self.text += f"Mini: {TAG.sub('', self.buf)}\n"
        self.render(""); self.busy = False; self.answered.emit()

    def on_fail(self, msg):
        self.text += f"[ошибка] {msg}\n"
        self.render(""); self.busy = False; self.answered.emit()

        print(msg)
    def render(self, current):
        self.log.setPlainText(self.text + (f"Мini: {current}" if current else ""))
        sb = self.log.verticalScrollBar(); sb.setValue(sb.maximum())