from lib.init import *
from widgets.dashboard_card import Card
from widgets.dashboard_func_card import FunctionalityCard
from backend.websocket import WSClient



class HomePage(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        
        self.mw = main_window
        
        self.emegency = False
        
        self.setStyleSheet("background-color: #f0f0f0; color: #8D30BD;")
        
        self.v = QtWidgets.QVBoxLayout()
        
        self.title_h = QtWidgets.QHBoxLayout()
        self.title = QtWidgets.QLabel("Dashboard")
        self.title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title.setStyleSheet("background-color: transparent;")
        self.title_h.addWidget(self.title, alignment=QtCore.Qt.AlignHCenter)
        
        self.dashboard = QtWidgets.QHBoxLayout()
        self.dashboard.addStretch()
        self.temp_card = Card("Temperature", "24°C")
        self.dashboard.addWidget(self.temp_card)
        self.humidity_card = Card("Humidity", "40%")
        self.dashboard.addWidget(self.humidity_card)
        self.lights_card = Card("Lights", "4 On")
        self.dashboard.addWidget(self.lights_card)
        self.security_card = Card("Security", "Closed")
        self.dashboard.addWidget(self.security_card)  
        self.dashboard.addStretch()      
        self.dashboard.setSpacing(40)
        self.dashboard.setContentsMargins(40, 40, 40, 40)
        
        
        self.title_h2 = QtWidgets.QHBoxLayout()
        self.title2 = QtWidgets.QLabel("Functions")
        self.title2.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title2.setStyleSheet("background-color: transparent;")
        self.title_h2.addWidget(self.title2, alignment=QtCore.Qt.AlignHCenter)
        
        self.body = QtWidgets.QWidget()
        
        self.funcs_h = QtWidgets.QHBoxLayout()
        self.p1 = FunctionalityCard("Temperature Graph", "icons/icons8-plot-50.png")
        self.p1.clicked.connect(lambda : self.MV(1))
        self.p2 = FunctionalityCard("Lights Control", "icons/icons8-external-lights-50.png")
        self.p2.clicked.connect(lambda: self.MV(3))
        self.p3 = FunctionalityCard("Door Security", "icons/icons8-door-sensor-checked-50")
        self.p3.clicked.connect(lambda: self.MV(4))
        self.funcs_h.addStretch()
        self.funcs_h.addWidget(self.p1)
        self.funcs_h.addWidget(self.p2)
        self.funcs_h.addWidget(self.p3)
        self.funcs_h.setSpacing(50)
        self.funcs_h.addStretch()
        # self.body.setFixedSize(900, 400)
        self.body.setStyleSheet("background-color:white;border: 2px solid transparent; border-radius: 10px;")
        self.body.setLayout(self.funcs_h)
        
        
        self.title_h3 = QtWidgets.QHBoxLayout()
        self.title3 = QtWidgets.QLabel("Emergency")
        self.title3.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title3.setStyleSheet("background-color: transparent;")
        self.title_h3.addWidget(self.title3, alignment=QtCore.Qt.AlignHCenter)
        
        self.emergency_h = QtWidgets.QHBoxLayout()
        self.emergency_btn = QtWidgets.QPushButton("Emergency (off)")
        self.emergency_btn.setFixedSize(150, 50)
        self.emergency_btn.setStyleSheet("background-color:red; border-radius: 10px;color:white;")
        self.emergency_btn.clicked.connect(self.send_emergency)
        self.emergency_h.addWidget(self.emergency_btn, alignment=QtCore.Qt.AlignHCenter)
        
        
        
        
        self.v.addLayout(self.title_h)
        self.v.addLayout(self.dashboard)
        self.v.addLayout(self.title_h2)
        self.v.addWidget(self.body, alignment=QtCore.Qt.AlignHCenter)
        self.v.addLayout(self.title_h3)
        self.v.addLayout(self.emergency_h)
        self.setLayout(self.v)
        
        self.worker = WSClient()
        self.worker.message_received.connect(self.update_data)
        self.worker.start()
        
    def MV(self, page):
        self.mw.changePage(page)
 
 
    def send_emergency(self, event):
        
            if self.emegency:
                msg = json.dumps({
                    "type": "emergency",
                        "data": {
                            "operation": 0
                        }
                })
                self.emegency = False
            else:
                msg = json.dumps({
                    "type": "emergency",
                        "data": {
                            "operation": 1
                        }
                })
                self.emegency = True
                
            self.worker.send_message.emit(msg)
        
    def resizeEvent(self, event):
        w = self.width() * 0.8   
        h = self.height() * 0.4
        # h = 300
        self.body.setFixedSize(w, h)
        super().resizeEvent(event)
    
    def update_data(self, text):
        
        data = json.loads(text)
        
        if data.get("type") == "dashboard":
        
            live_data = data.get("data")
            
            # count lights on ### UPDATED SERVER SENT COUNT ##
            # count = 0
            # for l in lights:
            #     if l == '1':
            #         count += 1
            self.temp_card.update(f"{live_data['temp']}°C")
            self.humidity_card.update(f"{live_data['hum']}%")
            self.lights_card.update(f"{str(live_data['lights'])} On")
            self.security_card.update(f"{'Closed' if live_data['security'] == 1 else 'Open'}")