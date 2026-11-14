from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import QWidget, QApplication
from pathlib import Path

image = Path(__file__).parent / 'cat.png'

class Pet(QWidget):
    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen()
        size = screen.size()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool

        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(size) # get_screen_resolution() возращает в tuple
        self.pix = QPixmap(image)

    def paintEvent(self, _):
        p = QPainter(self)
        p.drawPixmap(0, 0, self.pix)