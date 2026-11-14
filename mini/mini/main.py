import sys
from front.pet import Pet
from PySide6.QtWidgets import QApplication


app = QApplication(sys.argv)
pet = Pet() ; pet.show()
sys.exit(app.exec())
