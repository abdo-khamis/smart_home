import sys
from  PySide6 import QtWidgets ,QtCore
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QFont, QPixmap, QPainter, QBrush, QAction
from PySide6.QtCore import QThread, Signal,QDateTime, QPointF, Qt,QPropertyAnimation, Property,QTimer
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis,QDateTimeAxis
from PySide6 import QtGui
import asyncio
import websockets
import json
import sqlite3 as sql


from backend.init import *
from backend.funcs import *


db_cards = sql.connect("db/test.db")

cr = db_cards.cursor()

# cr.execute("update nfc_cards set label = '{label}' where id = {id}".format(label="Hello", id=1))
# db_cards.commit()



