from lib.init import *
from widgets.switch import Switch
from backend.websocket import WSClient

class RoomCard(QtWidgets.QFrame):
    COLOR_OFF = QColor("#FFFFFFFF")
    COLOR_ON = QColor("#8D30BD")
    COLOR_BORDER = QColor("#FFFFFFFF")
    LABEL_COLOR_ON = QColor("#FFFFFF")
    LABEL_COLOR_OFF = QColor("#8D30BD")

    def __init__(self, index, title="Room 1", parent=None):
        super().__init__(parent)
        self.is_on = False
        self._background_color = self.COLOR_OFF
        self.from_ws = False  
        
        self.index = index
        self.worker = WSClient()
        self.worker.start()

        self.setFixedSize(500, 100)
        self.setObjectName("RoomCard")
        self._update_style()

        self.title_label = QtWidgets.QLabel(title)
        font = self.title_label.font()
        font.setPointSize(14)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet(f"color: {self.COLOR_ON.name()}; border: none;")

        self.toggle = Switch()
        self.toggle.toggled.connect(self._handle_toggle)

        layout = QtWidgets.QHBoxLayout(self)
        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.title_label)
        top.addStretch()
        layout.addLayout(top)
        layout.addStretch()
        bottom = QtWidgets.QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(self.toggle)
        layout.addLayout(bottom)

        self.animation = QPropertyAnimation(self, b"backgroundColor")
        self.animation.setDuration(400)

    def _get_background_color(self):
        return self._background_color

    def _set_background_color(self, color):
        self._background_color = color
        self._update_style()
        
    def set_state(self, state: bool):
        """Update the toggle and color based on external data (e.g., from WebSocket)."""
        self.from_ws = True  
        self.toggle.setChecked(state)
        self._handle_toggle(state)
        self.from_ws = False  


    backgroundColor = Property(QColor, _get_background_color, _set_background_color)

    
    def _update_style(self):
        self.setStyleSheet(f"""
            #RoomCard {{
                background-color: {self._background_color.name()};
                border-radius: 15px;
            }}
        """)

    def animate_to(self, color):
        self.animation.stop()
        self.animation.setStartValue(self._background_color)
        self.animation.setEndValue(color)
        self.animation.start()

    def _handle_toggle(self, checked):
        self.is_on = checked
        target_color = self.COLOR_ON if checked else self.COLOR_OFF
        label_color = self.LABEL_COLOR_ON if checked else self.LABEL_COLOR_OFF
        
       
        if not self.from_ws:
            # msg = f"({self.index}, {checked})"
            msg = json.dumps({
                "type": "light_control",
                    "data": {
                        f"{self.index}": checked,
                    }
            })
            self.worker.send_message.emit(msg)
        
        self.title_label.setStyleSheet(f"color: {label_color.name()}; border: none;")

        self.animate_to(target_color)
