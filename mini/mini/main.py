import sys
from front.pet import Pet
from front.chat import ChatWindow
from PySide6.QtWidgets import QApplication
import os

os.environ['QT_QPA_PLATFORM'] = 'xcb' #запускает код в x11

app = QApplication(sys.argv)
pet = Pet() ; pet.show()
chat = ChatWindow()

pet.clicked.connect(chat.toggle)
chat.thinking.connect(lambda : pet.set_state("think", 90_000))
chat.action.connect(lambda tag: pet.set_state(tag, 4000))
chat.answered.connect(lambda: pet.set_state("idle", 2000))
sys.exit(app.exec())

