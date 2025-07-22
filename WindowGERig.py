import random
from pathlib import Path

from PyQt5.QtCore import QPoint, Qt, QRunnable, pyqtSlot, QThreadPool, QProcess, QTimer
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
        self.setFixedSize(110, 50)
        self.setContentsMargins(0, 0, 0, 0)

        typeColors = {"TE": "#FFA99B", "LTE": "#FF7C80", "DA": "#FFF2CC", "DD": "#FFE699", "SWS": "#BDD7EE", "RPM": "#C5E0B4", "MS": "#E0B4DB", "OTHER": "#9BFFA9"}
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
        groupbox.setFixedSize(90, 40)

        layout = QVBoxLayout()
        layout.addWidget(groupbox)

        self.setStyleSheet("QLabel{color: #434343};")
        self.boltFont = QFont()
        self.boltFont.setBold(True)

        self.smallFont = QFont('Arial', 10)

        self.nameLabel = QLabel(self.name, groupbox)
        self.nameLabel.setFont(self.boltFont)
        self.nameLabel.move(5, 0)
        self.nameLabel.setFixedSize(75, 20)

        self.valueLabel = QLabel("No Data", groupbox)
        self.valueLabel.setFont(self.smallFont)
        self.valueLabel.setAlignment(Qt.AlignRight)
        self.valueLabel.move(25, 20)
        self.valueLabel.setFixedSize(60, 20)

        self.unitLabel = QLabel(self.unit, groupbox)
        self.unitLabel.setFont(self.smallFont)
        self.unitLabel.setAlignment(Qt.AlignLeft)
        self.unitLabel.move(5, 20)
        self.unitLabel.setFixedSize(35, 20)

        self.setLayout(layout)

    def setValueText(self, value: str):
        self.valueLabel.setText(value)


class WindowGERig(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "GERig")

        self.lastData = {}

        msWidget = QGroupBox("Messstellenübersicht")
        self.mswid = msWidget
        scaleFactor = 1.0
        b, h = int(1500*scaleFactor), int(660*scaleFactor)
        msWidget.setFixedSize(b, h)
        backgroundLabel = QLabel()
        offset_x, offset_y = int(60*scaleFactor), int(80*scaleFactor)
        backgroundLabel.move(offset_x, offset_y)
        backgroundLabel.setScaledContents(True)
        backgroundLabel.setFixedSize(int(1400*scaleFactor), int(500*scaleFactor))
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

        offsetButton = QPushButton("Set Offset (delete prev.)", msWidget)
        offsetButton.move(x(0.85), y(0.03))
        offsetButton.clicked.connect(self.setOffset)

        deleteOffsetButton = QPushButton("Del Offset", msWidget)
        deleteOffsetButton.move(x(0.85), y(0.065))
        deleteOffsetButton.clicked.connect(self.delOffset)

        self.graphicalMeasurements = []
        # Raumlufttemperatur
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.260), y(0.080), "Geraet_G17_2_Kanal_75", "Temp RL", "°C", "LTE", x(0.328),y(0.110)))
        # Lufteinlass A
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.060), y(0.310), "Geraet_G17_2_Kanal_70", "Temp", "°C", "LTE", x(0.132), y(0.351)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.060), y(0.255), "Geraet_G17_2_Kanal_29", "p_a", "Pa", "DA", x(0.132), y(0.331)))
        # Lufteinlass B
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.679), y(0.245), "Geraet_G17_2_Kanal_71", "Temp", "°C", "LTE", x(0.716),y(0.342)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.679), y(0.190), "Geraet_G17_2_Kanal_30", "p_a", "Pa", "DA", x(0.716), y(0.322)))
        # Blende 5 (Zuluft)
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.770), y(0.100), "Geraet_G17_2_Kanal_33", "p_a (BL5)", "Pa", "DA", x(0.899),y(0.165)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.770), y(0.155), "Geraet_G17_2_Kanal_17", "p_d (BL5)", "Pa", "DD", x(0.899),y(0.185)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.830), y(0.100), "Geraet_G17_2_Kanal_46", "q_m (BL5)", "kg/s", "MS", x(0.910),y(0.165)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.830), y(0.155), "Geraet_G17_2_Kanal_67", "Temp (BL5)", "°C", "LTE", x(0.910),y(0.185)))
        # Blende 8 (Abluft)
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.000), y(0.110), "Geraet_G17_2_Kanal_35", "p_a (BL8)", "Pa", "DA", x(0.132),y(0.160)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.000), y(0.165), "Geraet_G17_2_Kanal_19", "p_d (BL8)", "Pa", "DD", x(0.132), y(0.180)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.060), y(0.110), "Geraet_G17_2_Kanal_48", "q_m (BL8)", "kg/s", "MS", x(0.143),y(0.160)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.060), y(0.165), "Geraet_G17_2_Kanal_69", "Temp (BL8)", "°C", "LTE", x(0.143), y(0.180)))
        # Blende 9 (Zuluft 0 Grad)
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.770), y(0.700), "Geraet_G17_2_Kanal_34", "p_a (BL9)", "Pa", "DA", x(0.899),y(0.728)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.770), y(0.755), "Geraet_G17_2_Kanal_18", "p_d (BL9)", "Pa", "DD", x(0.899),y(0.748)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.830), y(0.700), "Geraet_G17_2_Kanal_47", "q_m (BL9)", "kg/s", "MS", x(0.910),y(0.728)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.830), y(0.755), "Geraet_G17_2_Kanal_68", "Temp (BL9)", "°C", "LTE", x(0.910),y(0.748)))
        # RPM
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.180), y(0.280), "Geraet_G17_2_Kanal_3", "RPM", "rpm", "RPM", x(0.203),y(0.368)))
        # Schwingungssensoren
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.260), y(0.570), "Geraet_G17_2_Kanal_90", "SWS (Ax)", "mm/s", "SWS", x(0.253),y(0.603)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.647), y(0.505), "Geraet_G17_2_Kanal_65", "SWS (R)", "mm/s", "SWS", x(0.638),y(0.495)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.295), y(0.505), "Geraet_G17_2_Kanal_66", "SWS (R)", "mm/s", "SWS", x(0.325),y(0.495)))
        # Lagertemperaturen
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.250), y(0.210), "Geraet_G17_2_Kanal_81", "Temp FL1", "°C", "TE", x(0.266),y(0.320)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.340), y(0.210), "Geraet_G17_2_Kanal_80", "Temp FL2", "°C", "TE", x(0.390),y(0.320)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.605), y(0.240), "Geraet_G17_2_Kanal_82", "Temp LL", "°C", "TE", x(0.638),y(0.345)))
        # Luftplenum (0° & 50°)
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.760), y(0.500), "Geraet_G17_2_Kanal_39", "p_a (0°)", "Pa", "DA", x(0.817),y(0.335)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.840), y(0.500), "Geraet_G17_2_Kanal_40", "p_a (50°)", "Pa", "DA", x(0.830),y(0.335)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.760), y(0.555), "Geraet_G17_2_Kanal_83", "Temp (0°)", "°C", "LTE", x(0.817),y(0.355)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.840), y(0.555), "Geraet_G17_2_Kanal_84", "Temp (50°)", "°C", "LTE", x(0.830),y(0.355)))
        # Stator
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.470), y(0.040), "Geraet_G17_2_Kanal_62", "p_d (A-B)", "Pa", "DD", x(0.500),y(0.110)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.410), y(0.080), "Geraet_G17_2_Kanal_37", "p_a (Wall)", "Pa", "DA",x(0.497), y(0.206)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.400), y(0.215), "Geraet_G17_2_Kanal_77", "Temp R180", "°C", "LTE", x(0.468),y(0.247))) # 0.410), y(0.080
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.533), y(0.215), "Geraet_G17_2_Kanal_76", "Temp R180", "°C", "LTE", x(0.525),y(0.247)))
        # Stator Luft Temperatur
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.533), y(0.080), "Geraet_G17_2_Kanal_79", "Temp Air", "°C", "LTE", x(0.497), y(0.216)))
        # Innenwelle
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.545), y(0.490), "Geraet_T24_IW_Kanal_27", "p_a (IW)", "Pa", "DA", x(0.497),y(0.370)))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.545), y(0.545), "Geraet_T24_IW_Kanal_15", "Temp (IW)", "°C", "TE", x(0.509),y(0.408)))
        # Oel Einlauf A
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.170), y(0.220), "Geraet_G17_2_Kanal_72", "Temp (Oel)", "°C", "TE",x(0.178), y(0.360)))

        # Inflow Percent
        self.percentGraphicalMeasurements = GraphicalMeasurement(msWidget, x(0.880), y(0.440), "XXX", "%0° Inflow", "%", "OTHER", x(0.899),y(0.410))

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        if dataInfo["dataType"] =="CALIBRATED-Values":
            self.lastData[str(len(data["DATA"]))] = data

            # %0° Inflow GraphicalMeasurements
            if len(data["DATA"]) == 99:
                q1 = self.findCalibratedDataByUUID(data, dataInfo, "Geraet_G17_2_Kanal_46")
                q2 = self.findCalibratedDataByUUID(data, dataInfo, "Geraet_G17_2_Kanal_47")
                if q1 is not None and q2 is not None:
                    res = 0
                    if q1 > 0 and q2 > 0:
                        res = q2/q1 * 100
                    self.percentGraphicalMeasurements.setValueText(str("{0:6.1f}").format(res))
        for graphicalMeasurement in self.graphicalMeasurements:
            vData = self.findCalibratedDataByUUID(data, dataInfo, graphicalMeasurement.uuid)
            if vData is not None:
                graphicalMeasurement.setValueText(str("{0:6}").format(vData))

    def setOffset(self):
        if "99" in self.lastData.keys():
            self.setGlobalVarsEntry("BLENDEN_OFFSET", self.lastData["99"])

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
