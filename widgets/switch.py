from lib.init import *

class Switch(QtWidgets.QWidget):
    toggled = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 25)
        self._checked = False
        self._thumb_pos = 2

        self.animation = QPropertyAnimation(self, b"thumb_pos", self)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)

    def mousePressEvent(self, event):
        self.setChecked(not self._checked)
        self.toggled.emit(self._checked)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # الخلفية
        bg_color = QColor("#B94DEE") if self._checked else QColor("#777")
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)

        # الدائرة
        painter.setBrush(Qt.white)
        painter.drawEllipse(QtCore.QRectF(self._thumb_pos, 2, 21, 21))

    def _get_thumb_pos(self):
        return self._thumb_pos

    def _set_thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()

    thumb_pos = Property(float, _get_thumb_pos, _set_thumb_pos)

    def setChecked(self, state):
        self._checked = state
        start = 2 if not state else 27
        end = 27 if state else 2
        self.animation.stop()
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()