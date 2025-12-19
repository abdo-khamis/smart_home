from lib.init import *

class Card(QtWidgets.QWidget):

    def __init__(self, title, desc):
        super().__init__()

        self.setAttribute(Qt.WA_TranslucentBackground)


        wrapper_layout = QtWidgets.QVBoxLayout(self)
        wrapper_layout.setContentsMargins(20, 20, 20, 20) 

        card = QtWidgets.QFrame()
        card.setFixedSize(150, 100)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
            QLabel {
                color: #8D30BD;
                background-color: transparent; 
            }
        """)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 20)
        
        self.title_lbl = QtWidgets.QLabel(title)
        self.title_lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.title_lbl.setAlignment(Qt.AlignHCenter)
        
        self.desc_lbl = QtWidgets.QLabel(desc)
        self.desc_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setAlignment(Qt.AlignHCenter)

        


        layout.addWidget(self.title_lbl)
        layout.addStretch()
        layout.addWidget(self.desc_lbl)
        layout.addStretch()

        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 90))
        card.setGraphicsEffect(shadow)

        wrapper_layout.addWidget(card)

    def update(self, text):
        self.desc_lbl.setText(text)