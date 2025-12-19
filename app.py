from lib.init import *

from pages.HomePage import HomePage
from pages.TempPage import TempPage
from pages.ControlPage import ControlPage
from pages.SecurityPage import SecurityPage
from pages.ConnectionPage import ConnectionPage


class MainWindow(QtWidgets.QMainWindow):
    current_page = 0
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{app_name}")
        self.resize(800, 600)
        # self.setStyleSheet("background: transparent;")
        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)
        
        
        self.home = HomePage(self)
        self.temp = TempPage(self)
        self.check_from_connection = ConnectionPage(self)
        self.control = ControlPage(self)
        self.nfc = SecurityPage(self)
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.temp)
        self.stack.addWidget(self.check_from_connection)
        self.stack.addWidget(self.control)
        self.stack.addWidget(self.nfc)
        
        if get_ssid() == True:
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(2)
            
        
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_wifi_state)
        self.timer.start(5000)
        
    def update_wifi_state(self):
        ssid = get_ssid()
        
        if ssid:
            self.stack.setCurrentIndex(self.current_page)
        else:
            self.stack.setCurrentIndex(2)
    def changePage(self, index, duration=500):
        self.current_page = index
        
        if index == self.stack.currentIndex():
                return

        new_widget = self.stack.widget(index)


        if hasattr(self, "_current_anim") and self._current_anim is not None:
            try:
                self._current_anim.stop()
            except Exception:
                pass
            self._current_anim = None

        effect = QtWidgets.QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(effect)
        effect.setOpacity(0.0)

        self.stack.setCurrentWidget(new_widget)

        anim = QtCore.QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)

        def on_finished():
            try:
                new_widget.setGraphicsEffect(None)
            finally:
                self._current_anim = None

        anim.finished.connect(on_finished)
        self._current_anim = anim
        anim.start()
        
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())