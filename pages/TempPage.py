from lib.init import *
from backend.websocket import WSClient


class TempPage(QtWidgets.QWidget):
    label_color = QColor("#8D30BD")
    def __init__(self, main_window):
        super().__init__()

        self.mw = main_window
        self.series = QLineSeries()
        self.series.setName("Temperature")
        self.setStyleSheet("color: #8D30BD; background-color: #f0f0f0;")
        self.series.setColor("#8D30BD")

        # --- Chart setup ---
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.legend().show()
        self.chart.setTitle("Real-Time Temperature Throughout the Day")
        self.chart.setTitleBrush(self.label_color)
        self.chart.legend().setLabelBrush(QBrush(QColor("#8D30BD")))
        # --- Time axis (X) ---
        self.axis_x = QDateTimeAxis()
        self.axis_x.setFormat("hh:mm")
        self.axis_x.setTitleText("Time")
        self.axis_x.setTitleBrush(self.label_color)
        self.axis_x.setLabelsBrush(self.label_color)

        # اليوم الحالي
        start_of_day = QDateTime.currentDateTime().toSecsSinceEpoch() // 86400 * 86400
        start = QDateTime.fromSecsSinceEpoch(start_of_day)
        end = start.addSecs(24 * 3600)
        self.axis_x.setRange(start, end)

        # --- Temperature axis (Y) ---
        self.axis_y = QValueAxis()
        self.axis_y.setRange(10, 40)
        self.axis_y.setTitleText("Temperature (°C)")
        self.axis_y.setTitleBrush(self.label_color)
        self.axis_y.setLabelsBrush(self.label_color)
        self.axis_y.setLabelFormat("%.1f")

        # Attach axes
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)

        # --- Chart view ---
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        layout = QtWidgets.QVBoxLayout(self)
        
        self.backbtn = QtWidgets.QPushButton("Back")
        self.backbtn.setFixedSize(100, 35)
        self.backbtn.setCursor(QtCore.Qt.PointingHandCursor)
        self.backbtn.clicked.connect(self.back)
        layout.addWidget(self.backbtn, alignment=QtCore.Qt.AlignLeft)
        layout.addWidget(chart_view)


        
        self.worker = WSClient()
        self.worker.message_received.connect(self.update_chart)
        self.worker.start()

    def update_chart(self, msg):
        """Add real-time temperature reading to the chart."""
        
        data = json.loads(msg)
        
        if data.get("type") == "temp":
            
            temp_value = data.get("data")["temp"]    

            cr.execute("insert into temps (temp) values ({temp})".format(temp=temp_value))
            db_cards.commit()
            
            now = QDateTime.currentDateTime()
            self.series.append(now.toMSecsSinceEpoch(), temp_value)

            # Optional: Keep the chart auto-scrolling to current time
            self.axis_x.setMax(now)
            self.axis_x.setMin(now.addSecs(-3600))
    def back(self):
        self.mw.changePage(0)