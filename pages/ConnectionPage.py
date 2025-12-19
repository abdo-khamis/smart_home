from lib.init import *

class ConnectionPage(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        
        self.mw = main_window
        
        self.lay = QtWidgets.QVBoxLayout()
        self.h_2 = QtWidgets.QHBoxLayout()
        self.h_1 = QtWidgets.QHBoxLayout()
        
        
        self.text_h = QtWidgets.QLabel("Connection Error!")
        self.text_h.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.h_2.addStretch()
        self.h_2.addWidget(self.text_h)
        self.h_2.addStretch()
        
        self.h_3 = QtWidgets.QHBoxLayout()
        self.text_h3 = QtWidgets.QLabel("You Must Connect To SmartHome-Wifi To Continue.")
        self.text_h.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.h_3.addStretch()
        self.h_3.addWidget(self.text_h3)
        self.h_3.addStretch()
        
        
        self.btn = QtWidgets.QPushButton()
        self.btn.setText("Retry!")

        self.btn.setFixedSize(240, 60)
        self.btn.setStyleSheet(btn_style)
        self.btn.clicked.connect(self.mw.update_wifi_state)
        
        self.h_1.addWidget(self.btn)
        
        self.lay.addLayout(self.h_2)
        self.lay.addLayout(self.h_3)
        self.lay.addLayout(self.h_1)
        
        self.setLayout(self.lay)
        
