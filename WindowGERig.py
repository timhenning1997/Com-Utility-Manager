import random
from pathlib import Path

from PyQt5.QtCore import QPoint, Qt, QRunnable, pyqtSlot, QThreadPool, QProcess
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QDoubleSpinBox, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap, QFont
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from time import sleep


class GraphicalMeasurement(QWidget):
    def __init__(self, parent, x: int, y: int, uuid: str, name: str = "NAME", unit: str = "", type: str = "", indicatorCircleX: int = 0, indicatorCircleY: int = 0):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.uuid = uuid
        self.name = name
        self.unit = unit
        self.type = type
        self.indicatorCircleX = indicatorCircleX
        self.indicatorCircleY = indicatorCircleY
        self.color = "white"

        self.move(x, y)
        self.setFixedSize(100, 55)
        self.setContentsMargins(0, 0, 0, 0)

        typeColors = {"TE": "#FFA99B", "LTE": "#BDD7EE", "DA": "#FFF2CC", "DD": "#FFE699", "SWS": "#FF7C80", "RPM": "#C5E0B4"}
        if self.type in typeColors.keys():
            self.color = typeColors[self.type]

        self.indicatorCircle = QLabel()
        self.indicatorCircle.setParent(parent)
        self.indicatorCircle.move(self.indicatorCircleX, self.indicatorCircleY)
        self.indicatorCircle.setFixedSize(12, 12)
        self.indicatorCircle.setStyleSheet("QLabel{border: solid black; border-width: 2px; background-color: " + self.color + "; border-radius: 6;}")
        self.indicatorCircle.setContentsMargins(0, 0, 0, 0)

        groupbox = QGroupBox()
        groupbox.setStyleSheet("QGroupBox{background-color: " + self.color + "; border-radius: 10; border: solid #434343; border-width: 1px}")
        groupbox.setContentsMargins(0, 0, 0, 0)
        groupbox.setFixedSize(80, 45)

        layout = QVBoxLayout()
        layout.addWidget(groupbox)

        self.setStyleSheet("QLabel{color: #434343};")
        self.boltFont = QFont()
        self.boltFont.setBold(True)

        self.smallFont = QFont('Arial', 8)

        self.nameLabel = QLabel(self.name, groupbox)
        self.nameLabel.setFont(self.boltFont)
        self.nameLabel.move(5, 0)
        self.nameLabel.setFixedSize(60, 20)

        self.valueLabel = QLabel("No Data", groupbox)
        self.valueLabel.setFont(self.smallFont)
        self.valueLabel.setAlignment(Qt.AlignRight)
        self.valueLabel.move(25, 25)
        self.valueLabel.setFixedSize(50, 20)

        self.unitLabel = QLabel(self.unit, groupbox)
        self.unitLabel.setFont(self.smallFont)
        self.unitLabel.setAlignment(Qt.AlignLeft)
        self.unitLabel.move(5, 25)
        self.unitLabel.setFixedSize(35, 20)

        self.setLayout(layout)

    def setValueText(self, value: str):
        self.valueLabel.setText(value)


class WindowGERig(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "GERig")

        self.lastData = None

        msWidget = QGroupBox("Messstellenübersicht")
        b, h = 1500, 660
        msWidget.setFixedSize(b, h)
        backgroundLabel = QLabel()
        offset_x, offset_y = 60, 80
        backgroundLabel.move(offset_x, offset_y)
        backgroundLabel.setScaledContents(True)
        backgroundLabel.setFixedSize(1400, 500)
        pixmap = QPixmap(str(Path('res/Pictures/Betriebsmesstechnik_GE_Background.png')))
        backgroundLabel.setPixmap(pixmap)
        backgroundLabel.setParent(msWidget)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(msWidget)
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        def x(x_rel):
            return int((offset_x + b) * x_rel)

        def y(y_rel):
            return int((offset_y + h) * y_rel)

        offsetButton = QPushButton("Set Offset", msWidget)
        offsetButton.move(x(0.90), y(0.050))
        offsetButton.clicked.connect(self.setOffset)

        deleteOffsetButton = QPushButton("Del Offset", msWidget)
        deleteOffsetButton.move(x(0.90), y(0.10))
        deleteOffsetButton.clicked.connect(self.delOffset)

        self.graphicalMeasurements = []
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.787), y(0.415), "G16-1_Pruefsumme", "TLRT", "°C", "LTE", x(0.887), y(0.415)))

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        self.lastData = data
        for graphicalMeasurement in self.graphicalMeasurements:
            vData = self.findCalibratedDataByUUID(data, dataInfo, graphicalMeasurement.uuid)
            if vData is not None:
                graphicalMeasurement.setValueText(str("{0:6.1f}").format(vData))

    def setOffset(self):
        if self.lastData is not None:
            self.setGlobalVarsEntry("BLENDEN_OFFSET", self.lastData)

    def delOffset(self):
        globalVars = self.getGlobalVars()
        if "BLENDEN_OFFSET" in globalVars.keys():
            del globalVars["BLENDEN_OFFSET"]
            self.setGlobalVars(globalVars)

    def onClosing(self):
        pass

    def sendData(self):
        pass

    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        return ""

    def load(self, data):
        pass
