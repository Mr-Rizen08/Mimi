import sys
from front.pet import Pet
from PySide6.QtWidgets import QApplication
import os

os.environ['QT_QPA_PLATFORM'] = 'xcb' #запускает код в x11

app = QApplication(sys.argv)
pet = Pet() ; pet.show()
sys.exit(app.exec())
