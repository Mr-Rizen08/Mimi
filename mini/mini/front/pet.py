import json
import random
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QPainter, QTransform
from PySide6.QtWidgets import QWidget, QApplication
from pathlib import Path

root = Path(__file__).parent.parent / "assets" / "skins"
SCALE = 0.5
WEIGHTS = {
    "walk": 40, "idle": 15, "think": 15, "play": 10
}


def load_skin(name):
    image = root / name
    meta = json.loads((image / "skin.json").read_text(encoding="utf-8"))
    frames = {
        anim: [QPixmap(str(image / anim / f"{i:02}.PNG")) for i in range(n)]
        for anim, n in meta["frames"].items()
    }
    return frames, meta["fps"]


class Pet(QWidget):
    stateCharged = Signal(str)
    clicked = Signal()

    def __init__(self):
        super().__init__()

        screen = QApplication.primaryScreen()
        self.frames, fps = load_skin("cat") #возращает в tuple и передает frames[0], fps[1]
        pm = self.frames["idle"][0]
        self.resize(int(pm.width() * SCALE), int(pm.height() * SCALE))

        walk_screen = screen.availableGeometry()
        self.floor = walk_screen.bottom() - self.height() + 1
        self.move(walk_screen.left() + 200, self.floor)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool

        )
        self.brain = QTimer(self); self.brain.setSingleShot(True)
        self.brain.timeout.connect(self.pick); self.pick()


        self.state, self.i, self.dir = "idle", 0, 1
        self.tick = QTimer(); self.tick.timeout.connect(self._next); self.tick.start(1000 // fps )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.mover = QTimer(self); self.mover.timeout.connect(self._step); self.mover.start(16)

        self._press = None
        self._off = None
        self._dragging = False

    def _next(self):
        self.i =  (self.i + 1) % len(self.frames[self.state]); self.update()


    def _step(self):
        if self.state != "walk": return
        s = QApplication.primaryScreen().availableGeometry()
        x = self.x() + 2 * self.dir
        if x < s.left():
            x, self.dir = s.left(), 1
        if x > s.right() - self.width():
            x, self.dir = s.right() - self.width(), -1
        self.move(x, self.floor)

    def set_state(self, s, ms=3000):
        self.state, self.i = s, 0
        if s == "walk": self.dir = random.choice([1, -1])
        self.brain.start(ms)
        self.stateCharged.emit(s)


    def pick(self):
        s = random.choices(list(WEIGHTS), list(WEIGHTS.values()))[0]
        self.set_state(s, random.randint(2500, 6000))

    def paintEvent(self, _):
        pm = self.frames[self.state][self.i  % len(self.frames[self.state])]
        if self.dir < 0:
            pm  = pm.transformed(QTransform().scale(-1, 1))
        p = QPainter(self)
        p.setRenderHints(QPainter.RenderHint.SmoothPixmapTransform) # сглаживание
        w = int(pm.width() * SCALE)
        h = int(pm.height() * SCALE)
        p.drawPixmap(0, 0, w, h,  pm)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton: return
        self._press = e.globalPosition().toPoint(); self._moved = False
        self._off = self._press - self.pos()
        self._dragging = False

    def mouseMoveEvent(self, e):
        if self._press is None: return
        p = e.globalPosition().toPoint()
        if not self._dragging and (p - self._press).manhattanLength() < 5:
            return
        self._dragging = True
        self.move(p- self._off)

    def mouseReleaseEvent(self, e):
        if self._press is None: return
        if self._dragging:
            self.floor = self.y()
        else:
            self.clicked.emit()
        self._press = None
        self._dragging = False





