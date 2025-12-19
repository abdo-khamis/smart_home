from lib.init import *
from widgets.room_card import RoomCard
from backend.websocket import WSClient

class ControlPage(QtWidgets.QWidget):
    def __init__(self, mw):
        super().__init__()
        self.mw =mw
        self.setStyleSheet("color: #8D30BD;")
        
        self.worker = WSClient()
        self.worker.message_received.connect(self.getData)
        self.worker.start()
        
        
        self.card1 = RoomCard(22,"Living Room")
        self.card2 = RoomCard(12,"Room 1")
        self.card3 = RoomCard(13,"Room 2")
        self.card4 = RoomCard(4,"Room 3")
        
        
        
        layout = QtWidgets.QVBoxLayout(self)
        
        self.backbtn = QtWidgets.QPushButton("Back")
        self.backbtn.setFixedSize(100, 35)
        self.backbtn.setCursor(QtCore.Qt.PointingHandCursor)
        self.backbtn.clicked.connect(self.back)
        layout.addWidget(self.backbtn, alignment=QtCore.Qt.AlignLeft)     
        layout.addWidget(self.card1, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.card2, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.card3, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.card4, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def resizeEvent(self, event):
        w = self.width() * 0.9   
        h = 100
        # h = 300
        self.card1.setFixedSize(w, h)
        self.card2.setFixedSize(w, h)
        self.card3.setFixedSize(w, h)
        self.card4.setFixedSize(w, h)
        super().resizeEvent(event)
        
    def back(self):
        self.mw.changePage(0)
        
    def getData(self, txt):
        
        data = json.loads(txt)
        
        if data.get("type") == "lights_control":
            parts = data.get("data")
            self.card1.set_state(int(parts["1"]))
            self.card2.set_state(int(parts["2"]))
            self.card3.set_state(int(parts["3"]))
            self.card4.set_state(int(parts["4"]))


