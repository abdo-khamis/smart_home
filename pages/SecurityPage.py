from lib.init import *
import uuid
from backend.websocket import *
import datetime



class ToastNotification(QtWidgets.QWidget):
    def __init__(self, message, color="#4CAF50", duration=3000, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.label = QtWidgets.QLabel(message, self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 14px;
        """)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        
        QtCore.QTimer.singleShot(duration, self.close)
    
    def show_near(self, parent_widget):
        if parent_widget:
            geo = parent_widget.geometry()
            self.adjustSize()
            self.move(
                geo.center().x() - self.width() // 2,
                geo.top()
            )
        self.show()


class EditDialog(QtWidgets.QDialog):
    """A simple dialog to get a new name from the user."""

    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Name")
        self.setMinimumWidth(300)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel("Enter the new name:")
        self.name_input = QtWidgets.QLineEdit(current_name)
        self.submit_button = QtWidgets.QPushButton("Submit")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.submit_button)

        self.submit_button.clicked.connect(self.accept)

    def get_name(self):
        """Returns the text from the input field."""
        return self.name_input.text()


class NFCCard(QtWidgets.QWidget):
    def __init__(self,db_id, name, nfc_number, added_date, last_access, parent=None):
        super().__init__(parent)
        self.page = parent
        self.current_name = name
        self.db_id = db_id
        self.last_access_time = None
        self.setup_ui(name, nfc_number, added_date, last_access)

    def setup_ui(self, name, nfc_number, added_date, last_access):
        self.setFixedSize(350, 180)

        # --- Main layout (holds the white frame) ---
        wrapper_layout = QtWidgets.QVBoxLayout(self)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        # --- Frame that will act as the white card background ---
        frame = QtWidgets.QFrame()
        frame.setObjectName("card_frame")
        frame.setStyleSheet("""
            QFrame#card_frame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #CCCCCC;
            }
        """)
        inner_layout = QtWidgets.QVBoxLayout(frame)
        inner_layout.setContentsMargins(20, 15, 20, 15)

        # --- Top layout ---
        top_layout = QtWidgets.QHBoxLayout()
        self.name_label = QtWidgets.QLabel(name)
        self.name_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.name_label.setStyleSheet("color: #8D30BD;background-color:transparent;")

        self.options_button = QtWidgets.QPushButton("...")
        self.options_button.setFixedSize(30, 30)
        self.options_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.options_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border-radius: 15px;
                
            }
            QPushButton::menu-indicator {
                        image: none;  
                        width: 0px;
            }
            QPushButton:hover {
                background-color: #f9f9f9;
            }
        """)
        self.setup_menu()

        top_layout.addWidget(self.name_label)
        top_layout.addStretch()
        top_layout.addWidget(self.options_button)

        # --- Bottom layout ---
        bottom_layout = QtWidgets.QHBoxLayout()
        left_details = QtWidgets.QVBoxLayout()
        right_details = QtWidgets.QVBoxLayout()

        nfc_label = QtWidgets.QLabel("NFC Number")
        nfc_label.setStyleSheet("color: #8D30BD;background-color:transparent; font-size: 11px;")
        self.nfc_value = QtWidgets.QLabel(nfc_number)
        self.nfc_value.setStyleSheet("color: #8D30BD;background-color:transparent; font-size: 14px;")

        added_label = QtWidgets.QLabel("Added Date")
        added_label.setStyleSheet("color: #8D30BD;background-color:transparent; font-size: 11px; margin-top: 10px;")
        self.added_value = QtWidgets.QLabel(added_date)
        self.added_value.setStyleSheet("color: #8D30BD;background-color:transparent; font-size: 14px;")

        left_details.addWidget(nfc_label)
        left_details.addWidget(self.nfc_value)
        left_details.addWidget(added_label)
        left_details.addWidget(self.added_value)

        last_access_label = QtWidgets.QLabel("Last Access")
        last_access_label.setStyleSheet("color: #8D30BD;background-color:transparent; font-size: 11px;")
        self.last_access_value = QtWidgets.QLabel(last_access)
        self.last_access_value.setStyleSheet("color: #8D30BD;background-color:transparent; font-size: 14px;")

        right_details.addWidget(last_access_label)
        right_details.addWidget(self.last_access_value)

        bottom_layout.addLayout(left_details)
        bottom_layout.addStretch()
        bottom_layout.addLayout(right_details)

        # --- Assemble layouts ---
        inner_layout.addLayout(top_layout)
        inner_layout.addStretch()
        inner_layout.addLayout(bottom_layout)
        wrapper_layout.addWidget(frame)

        

    def setup_menu(self):
        """Creates the context menu for the options button."""
        self.menu = QtWidgets.QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background-color: white;
                color: #8D30BD;
                border: 1px solid #555555;
            }
            QMenu::item:selected {
                background-color: #556677;
            }
        """)
        
        edit_action = QAction("Edit", self)
        delete_action = QAction("Delete", self)

        edit_action.triggered.connect(self.edit_card)
        delete_action.triggered.connect(self.delete_card)

        self.menu.addAction(edit_action)
        self.menu.addAction(delete_action)

        self.options_button.setMenu(self.menu)
        
    def edit_card(self):
        """Opens a dialog to edit the card's name."""
        dialog = EditDialog(self.current_name, self)
        
        if dialog.exec():  # exec() returns true if the dialog was accepted
            new_name = dialog.get_name()
            if new_name:
                self.current_name = new_name
                self.name_label.setText(new_name)
                cr.execute("update nfc_cards set label = '{label}' where id = {card_id}".format(label=new_name, card_id=self.db_id))
                db_cards.commit()

    def delete_card(self):
        """Placeholder for delete functionality."""
        cr.execute("delete from nfc_cards where id = {card_id}".format(card_id=self.db_id))
        db_cards.commit()
        
        if self.page:
            layout = self.page.grid
            layout.removeWidget(self)
            

            if self in self.page.cards:
                self.page.cards.remove(self)

        self.deleteLater()

    def update_last_access(self, time_str):
        """تحديث الوقت المعروض وتخزينه."""
        self.last_access_value.setText(time_str)
        try:
            self.last_access_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except:
            self.last_access_time = None    
# ----------------------------------------------------------
# Dialog that appears when pressing "Add"
# ----------------------------------------------------------
class AddMethodDialog(QtWidgets.QDialog):
    method_selected = QtCore.Signal(str)  # "rfid" or "manual"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New NFC")
        self.setFixedSize(300, 150)
        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Select method to add NFC:")
        label.setAlignment(QtCore.Qt.AlignCenter)

        rfid_btn = QtWidgets.QPushButton("From RFID Scanner")
        manual_btn = QtWidgets.QPushButton("Add Manually")

        for btn in [rfid_btn, manual_btn]:
            btn.setFixedHeight(40)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #8D30BD;
                    color: white;
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #A847D8; }
            """)

        rfid_btn.clicked.connect(lambda: self.method_selected.emit("rfid"))
        manual_btn.clicked.connect(lambda: self.method_selected.emit("manual"))

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(rfid_btn)
        layout.addWidget(manual_btn)
        layout.addStretch()

# ----------------------------------------------------------
# SecurityPage with top bar and grid
# ----------------------------------------------------------
class SecurityPage(QtWidgets.QWidget):
    def __init__(self, mw, ):
        super().__init__()
        self.mw = mw

        self.worker = WSClient()
        self.worker.message_received.connect(self.check_msg)
        self.worker.start()

        self.data_nfc = cr.execute("select * from nfc_cards").fetchall()
        self.cards = []
        self.loop = asyncio.get_event_loop()

        self.init_ui()

    def init_ui(self):
        # self.setStyleSheet("background-color: #EAEAEA;")
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_last_access_times)
        self.timer.start(1000)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # -------------------- TOP BAR --------------------
        top_bar = QtWidgets.QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(10)

        self.back_btn = QtWidgets.QPushButton("← Back")
        self.back_btn.clicked.connect(self.back)
        self.add_btn = QtWidgets.QPushButton("+ Add")

        for btn in [self.back_btn, self.add_btn]:
            btn.setFixedSize(100, 35)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setStyleSheet("""
                    color: #8D30BD; 
            """)

        top_bar.addWidget(self.back_btn, alignment=QtCore.Qt.AlignLeft)
        top_bar.addStretch()
        top_bar.addWidget(self.add_btn, alignment=QtCore.Qt.AlignRight)
        main_layout.addLayout(top_bar)

        # -------------------- SCROLL GRID --------------------
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.container = QtWidgets.QWidget()
        self.container.setStyleSheet("background-color:white")
        self.grid = QtWidgets.QGridLayout(self.container)
        self.grid.setSpacing(20)
        self.grid.setContentsMargins(20, 20, 20, 20)

        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)

        # -------------------- CONNECTIONS --------------------
        self.add_btn.clicked.connect(self.show_add_dialog)
        
        
        for card in self.data_nfc:
            self.add_card(card[1], str(card[2]), card[3], card[4], card[0])

    # ------------------------------------------------------
    def show_add_dialog(self):
        dialog = AddMethodDialog(self)
        dialog.method_selected.connect(self.handle_add_method)
        dialog.exec()

    # ------------------------------------------------------
    def handle_add_method(self, method):
        if method == "rfid":
            self.request_from_rfid()
        elif method == "manual":
            self.add_card_manually()

    # ------------------------------------------------------
    def back(self):
        self.mw.changePage(0)
    def add_card_manually(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Manual Add", "Enter NFC number:")
        if ok and text:
            label = f"Manual User{uuid.uuid4()}"
            cr.execute("insert into nfc_cards (label, nfc_number) values ('{label}', '{nfc_number}')".format(label=label, nfc_number=text))
            db_cards.commit()
            
            id_from_db = cr.execute("select * from nfc_cards where nfc_number = '{nfc_number}'".format(nfc_number=text)).fetchone()[0]

            self.add_card(label, text, f"{datetime.datetime.date(datetime.datetime.now())}", "None", id_from_db)
    
    def update_last_access_times(self):
        now = datetime.datetime.now()
        for card in self.cards:
            if card.last_access_time:
                diff = now - card.last_access_time
                seconds = int(diff.total_seconds())

                if seconds < 60:
                    text = f"Few Seconds"
                elif seconds < 3600:
                    minutes = seconds // 60
                    text = f"{minutes} Minutes"
                elif seconds < 86400:
                    hours = seconds // 3600
                    text = f"{hours} Hour"
                else:
                    days = seconds // 86400
                    text = f"{days} Day"

                card.last_access_value.setText(text)

    # ------------------------------------------------------
    def add_card(self, name, nfc, added, last, db_id):
        card = NFCCard(db_id,name, nfc, added, last ,parent=self)
        row = len(self.cards) // 2
        col = len(self.cards) % 2
        self.grid.addWidget(card, row, col, QtCore.Qt.AlignCenter)
        self.cards.append(card)
        
    def request_from_rfid(self):
        msg = json.dumps({
            'type':'security_control',
            "data": {
                 "data_type": "add_request"
            }
        })
        self.worker.send_message.emit(msg)
    def check_msg(self, msg):
        try:
            data = json.loads(msg)
            print(data)
            if data.get("type") == "security":
                inner = data.get("data", {})
                if inner.get("data_type") == "new_nfc":
                    nfc_num = str(inner.get("nfc_number"))
                    print(nfc_num)
                    label = f"New User-{uuid.uuid4()}"
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    cr.execute("insert into nfc_cards (label, nfc_number,last_access) values ('{label}', '{nfc_number}', '{now}')".format(label=label, nfc_number=nfc_num, now=now))
                    db_cards.commit()
                    
                    id_from_db = cr.execute("select * from nfc_cards where nfc_number = '{nfc_number}'".format(nfc_number=nfc_num)).fetchone()[0]
                    
                    self.add_card(label, nfc_num, f"{datetime.datetime.date(datetime.datetime.now())}", now, id_from_db)
                    
                    print(f" New NFC received and added: {nfc_num}")
                elif inner.get("data_type") == "access":
                    nfc_num = str(inner.get("nfc_number"))
                    
                    check_nfc = cr.execute("select * from nfc_cards where nfc_number = '{nfc_number}'".format(nfc_number=nfc_num)).fetchone()
                    
                    if check_nfc:
                        msg = json.dumps({
                            "type": "security_control",
                            "data": {
                                "data_type": "access_request",
                                "response": 200
                            }
                        })
                        self.worker.send_message.emit(msg)
                        
                        cr.execute("update nfc_cards set label = '{label}' where nfc_number ='{nfc_number}'".format(label=check_nfc[1], nfc_number=check_nfc[2]))
                        db_cards.commit()
                        
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        for card in self.cards:
                            if card.nfc_value.text() == nfc_num:
                                card.update_last_access(now)
                                break
                            
                        ToastNotification("Access Granted ", "#4CAF50", 3000, self).show_near(self)

                    else:
                        msg = json.dumps({
                            "type": "security_control",
                            "data": {
                                "data_type": "access_request",
                                "response": 400
                            }
                        })
                        self.worker.send_message.emit(msg)
                        
                        ToastNotification("Access Denied ", "#F44336", 3000, self).show_near(self)

                else:
                    pass
                    # print(" Unknown data_type in security:", inner.get("data_type"))
            else:
                # print(" Unknown message type:", data.get("type"))
                pass

        except Exception as e:
            # print(" Error while parsing message:", e)

            pass
