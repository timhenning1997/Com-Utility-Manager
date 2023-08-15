from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap, QFont
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters


class GraphicalMeasurement(QWidget):
    def __init__(self, parent, x: int, y: int, uuid: str, name: str = "NAME", unit: str = "", type: str = ""):
        super().__init__(parent)

        self.move(x, y)
        self.setFixedSize(100, 55)
        self.setContentsMargins(0, 0, 0, 0)

        self.uuid = uuid
        self.name = name
        self.unit = unit
        self.type = type

        if self.type == "TE":
            self.color = "#FFA99B"
        elif self.type == "LTE":
            self.color = "#BDD7EE"
        elif self.type == "DA":
            self.color = "#FFF2CC"
        elif self.type == "DD":
            self.color = "#FFE699"
        elif self.type == "SWS":
            self.color = "#FF7C80"
        elif self.type == "RPM":
            self.color = "#C5E0B4"
        else:
            self.color = "black"
        

        groupbox = QGroupBox()
        groupbox.setStyleSheet("QGroupBox{background-color: "+self.color+"; border-radius: 10;}")
        groupbox.setContentsMargins(0, 0, 0, 0)
        groupbox.setFixedSize(80, 45)

        layout = QVBoxLayout()
        layout.addWidget(groupbox)

        self.nameLabel = QLabel(self.name, groupbox)
        self.setStyleSheet("QLabel{color: #434343};")
        myFont=QFont()
        myFont.setBold(True)
        self.nameLabel.setFont(myFont)
        self.nameLabel.move(5, 0)
        self.nameLabel.setFixedSize(60, 20)

        self.valueLabel = QLabel("No Data", groupbox)
        self.valueLabel.setAlignment(Qt.AlignLeft)
        self.valueLabel.move(5, 25)
        self.valueLabel.setFixedSize(50, 20)

        self.unitLabel = QLabel(self.unit, groupbox)
        self.unitLabel.setAlignment(Qt.AlignRight)
        self.unitLabel.move(40, 25)
        self.unitLabel.setFixedSize(35, 20)

        self.setLayout(layout)

    def setValueText(self, value: str):
        self.valueLabel.setText(value)

class WindowBetriebsmesstechnik(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "Betriebsmesstechnik")

        # Dem Hauptfenster ein Layout zuweisen
        massestromGridLayout = QGridLayout()
        druckversorgungGridLayout = QGridLayout()
        betriebsspannungGridLayout = QGridLayout()
        legendeGridLayout = QGridLayout()
        msWidget = QGroupBox("Messstellenübersicht")
        subLayout = QVBoxLayout()
        mainLayout = QHBoxLayout()

        massestromGridLayout.addWidget(QLabel("BL1 (MH zu)"), 0,0)
        massestromGridLayout.addWidget(QLabel("BL3 (ZKMR ab)"), 1,0)
        massestromGridLayout.addWidget(QLabel("BL9 (ZKMR zu)"), 2,0)
        massestromGridLayout.addWidget(QLabel("xx,xx (\u00B1 x,x %)"), 0,1)
        massestromGridLayout.addWidget(QLabel("xx,xx (\u00B1 x,x %)"), 1,1)
        massestromGridLayout.addWidget(QLabel("xx,xx (\u00B1 x,x %)"), 2,1)
        massestromGridLayout.addWidget(QLabel("kg/s"), 0,2)
        massestromGridLayout.addWidget(QLabel("kg/s"), 1,2)
        massestromGridLayout.addWidget(QLabel("kg/s"), 2,2)
        massestromGridLayout.setColumnStretch(0,3)
        massestromGridLayout.setColumnStretch(1,2)
        massestromGridLayout.setColumnStretch(2,1)

        betriebsspannungGridLayout.addWidget(QLabel("Telemetrie A"), 0,0)
        betriebsspannungGridLayout.addWidget(QLabel("Telemetrie B"), 1,0)
        betriebsspannungGridLayout.addWidget(QLabel("Telemetrie IW"), 2,0)
        betriebsspannungGridLayout.addWidget(QLabel("xx,xx"), 0,1)
        betriebsspannungGridLayout.addWidget(QLabel("xx,xx"), 1,1)
        betriebsspannungGridLayout.addWidget(QLabel("xx,xx"), 2,1)
        betriebsspannungGridLayout.addWidget(QLabel("V"), 0,2)
        betriebsspannungGridLayout.addWidget(QLabel("V"), 1,2)
        betriebsspannungGridLayout.addWidget(QLabel("V"), 2,2)
        betriebsspannungGridLayout.setColumnStretch(0,3)
        betriebsspannungGridLayout.setColumnStretch(1,2)
        betriebsspannungGridLayout.setColumnStretch(2,1)

        druckversorgungGridLayout.addWidget(QLabel("Vordruck"), 0,0)
        druckversorgungGridLayout.addWidget(QLabel("Filterdruck"), 1,0)
        druckversorgungGridLayout.addWidget(QLabel("xx,xx"), 0,1)
        druckversorgungGridLayout.addWidget(QLabel("xx,xx"), 1,1)
        druckversorgungGridLayout.addWidget(QLabel("bar"), 0,2)
        druckversorgungGridLayout.addWidget(QLabel("kPa"), 1,2)
        druckversorgungGridLayout.setColumnStretch(0,3)
        druckversorgungGridLayout.setColumnStretch(1,2)
        druckversorgungGridLayout.setColumnStretch(2,1)

        piclist = [
            ['res\\pics\\Messstelle_Temperatur.png', "Materialtemperatur"],
            ['res\\pics\\Messstelle_Lufttemperatur.png', "Lufttemperatur"],
            ['res\\pics\\Messstelle_Druck_absolut.png', "Absolutdruck"],
            ['res\\pics\\Messstelle_Druck_differenz.png', "Differenzdruck"],
            ['res\\pics\\Messstelle_Schwinggeschwindigkeit.png', "Schwinggeschwindigkeit"],
            ['res\\pics\\Messstelle_Magnet.png', "Magnet (Signalgeber)"],
            ['res\\pics\\Messstelle_Hallgeber.png',"Hallsensor (Drehfrequenz)"],
            ['res\\pics\\Messstelle_Blende.png',"Normblende"]
            ]

        for num in range(0, len(piclist)):
            symbolLabel = QLabel()
            pixmap = QPixmap(piclist[num][0])
            symbolLabel.setPixmap(pixmap)
            # symbolLabel.setScaledContents(True)
            # symbolLabel.setFixedSize(15,15)
            legendeGridLayout.addWidget(symbolLabel, num, 0, alignment=Qt.AlignCenter)
            legendeGridLayout.addWidget(QLabel(piclist[num][1]), num, 1)
            

        massestromGroubox = QGroupBox("Massestrom")
        druckversorgungGroubox = QGroupBox("Druckversorgung")
        betriebsspannungGroupbox = QGroupBox("Betriebsspannung")
        legendeGroubox = QGroupBox("Legende")
        msWidget.setStyleSheet("QGroupBox {font-size: 16px;}") 
        massestromGroubox.setStyleSheet("QGroupBox {font-size: 16px;}") 
        druckversorgungGroubox.setStyleSheet("QGroupBox {font-size: 16px;}") 
        betriebsspannungGroupbox.setStyleSheet("QGroupBox {font-size: 16px;}") 
        legendeGroubox.setStyleSheet("QGroupBox {font-size: 16px;}") 

        massestromGroubox.setLayout(massestromGridLayout)
        druckversorgungGroubox.setLayout(druckversorgungGridLayout)
        betriebsspannungGroupbox.setLayout(betriebsspannungGridLayout)
        legendeGroubox.setLayout(legendeGridLayout)

        subLayout.addWidget(massestromGroubox)
        subLayout.addWidget(druckversorgungGroubox)
        subLayout.addWidget(betriebsspannungGroupbox)
        subLayout.addWidget(legendeGroubox)
        # subLayout.addStretch()
        massestromGroubox.setFixedHeight(120)
        druckversorgungGroubox.setFixedHeight(90)
        betriebsspannungGroupbox.setFixedHeight(120)
        legendeGroubox.setFixedHeight(240)

        mainLayout.addWidget(msWidget)
        mainLayout.addLayout(subLayout)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        msWidget.setFixedSize(920,660)
        backgroundLabel = QLabel(msWidget)
        backgroundLabel.move(60, 80)
        backgroundLabel.setScaledContents(True)
        backgroundLabel.setFixedSize(800,600)
        pixmap = QPixmap('res\\pics\\Betriebsmesstechnik _Messstellen.png')
        backgroundLabel.setPixmap(pixmap)
        

        self.graphicalMeasurements = []
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget,   0,  50, "UUID", "TLRT", "°C", "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget,   0, 130, "UUID", "TLSBL9", "°C", "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget,   0, 180, "UUID", "DDSBL9", "kPa", "DD"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget,   0, 230, "UUID", "DSBL9", "bar", "DA"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget,   0, 310, "UUID", "TLSA", "bar", "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget,   0, 405, "UUID", "DSA", "bar", "DA"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 152, 250, "UUID", "RPM", "rpm", "RPM"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 152, 200, "UUID", "TSA2", "°C", "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 152, 150, "UUID", "TSA1", "°C", "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 152, 100, "G16.1_SPI_6", "SWA", "mm/s", "SWS"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 247, 250, "G16.1_SPI_0", "GTARA2", "°C", "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 247, 200, "UUID", "GTARA1", "°C", "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 247, 150, "G16.1_SPI_2", "LTKR", "°C", "LTE"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 285,  50, "G16.1_SPI_1", "GTMRaA", "°C", "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 285, 100, "UUID", "GTMRbA", "°C", "TE"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 380,   0, "UUID", "TLSBL1", "°C", "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 380,  50, "UUID", "DDSBL1", "kPa", "DD"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 380, 100, "UUID", "DSBL1", "bar", "DA"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 530,  50, "G16.1_SPI_3", "GTMRaB", "°C", "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 530, 100, "UUID", "GTMRbB", "°C", "TE"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 585, 250, "G16.1_SPI_4", "GTARB2", "°C", "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 585, 200, "UUID", "GTARB1", "°C", "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 585, 150, "UUID", "LPKR", "°C", "DA"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 670, 200, "UUID", "TSB1", "°C", "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 670, 250, "G16.1_SPI_7", "SWB", "mm/s", "SWS"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 690, 470, "G16.1_SPI_5", "TOelZu", "°C", "LTE"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 820, 130, "UUID", "TLSBL3", "°C", "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 820, 180, "UUID", "DDSBL3", "kPa", "DD"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 820, 230, "UUID", "DSBL3", "bar", "DA"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 820, 320, "UUID", "TLSB", "bar", "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, 820, 390, "UUID", "DSB", "bar", "DA"))



    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        for graphicalMeasurement in self.graphicalMeasurements:
            
            vData = self.findCalibratedDataByUUID(data, dataInfo, graphicalMeasurement.uuid)
            if vData is not None:
                graphicalMeasurement.setValueText(str("{0:10.2f}").format(vData))

    def sendData(self):
        # self.sendSerialData() ist eine interne Funktion, die die activen Ports berücksichtigt
        self.sendSerialData("sending test data...")

    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        return ""

    def load(self, data):
        pass
