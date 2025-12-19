from lib.init import *

class FunctionalityCard(QtWidgets.QWidget):
    clicked = QtCore.Signal()
    def __init__(self, text, img_path):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        wrapper_layout = QtWidgets.QVBoxLayout(self)
        wrapper_layout.setContentsMargins(20, 20, 20, 20) 

        card = QtWidgets.QFrame()
        card.setFixedSize(150, 150)
        card.setStyleSheet("""
            QFrame {
                background-color: #fff7f7;
                border-radius: 15px;
            }
            QLabel {
                color: #8D30BD;
                background-color: transparent; 
            }
        """)

        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 20)
        
        title_lbl = QtWidgets.QLabel(text)
        title_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_lbl.setAlignment(Qt.AlignHCenter)
        
        
        img_lbl = QtWidgets.QLabel()
        img_lbl.setAlignment(Qt.AlignHCenter)
        img = QPixmap(img_path)


        img_lbl.setPixmap(img)
        # img_lbl.setScaledContents(True)
        

        layout.addWidget(title_lbl)
        layout.addWidget(img_lbl)
        
        wrapper_layout.addWidget(card)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()  # trigger the signal
        super().mousePressEvent(event)

