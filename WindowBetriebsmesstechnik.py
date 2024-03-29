from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QGroupBox, QHBoxLayout, QGridLayout, QFileDialog
from PyQt5.QtGui import QPixmap, QFont, QIcon
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from UsefulFunctions import resource_path
from Blendenmessung import Blendenmessung
from pathlib import Path
import json, sys, os


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
        self.boltFont=QFont()
        self.boltFont.setBold(True)
        self.nameLabel.setFont(self.boltFont)
        self.nameLabel.move(5, 0)
        self.nameLabel.setFixedSize(60, 20)

        self.smallFont=QFont('Arial', 8)

        self.valueLabel = QLabel("No Data", groupbox)
        self.valueLabel.setFont(self.smallFont)
        self.valueLabel.setAlignment(Qt.AlignRight)
        self.valueLabel.move(25, 25)
        self.valueLabel.setFixedSize(50, 20)

        self.unitLabel = QLabel(self.unit, groupbox)
        self.unitLabel .setFont(self.smallFont)
        self.unitLabel.setAlignment(Qt.AlignLeft)
        self.unitLabel.move(5, 25)
        self.unitLabel.setFixedSize(35, 20)

        self.setLayout(layout)

    def setValueText(self, value: str):
        self.valueLabel.setText(value)

class WindowBetriebsmesstechnik(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "Betriebsmesstechnik")

        self.offsetFlag = False
        self.useOffset = True

        # Dem Hauptfenster ein Layout zuweisen
        massestromGridLayout = QGridLayout()
        druckversorgungGridLayout = QGridLayout()
        betriebsspannungGridLayout = QGridLayout()
        fehlerGridLayout = QGridLayout()
        msWidget = QGroupBox("Messstellenübersicht")
        subLayout = QHBoxLayout()
        DruckBeriebsspannungLayout = QVBoxLayout()
        MassestromBlendenkonfigLayout = QVBoxLayout()
        mainLayout = QVBoxLayout()

        self.label_BL1 = QLabel("xx,xx (\u00B1 x,x %)")
        self.label_BL3 = QLabel("xx,xx (\u00B1 x,x %)")
        self.label_BL7 = QLabel("xx,xx (\u00B1 x,x %)")
        self.label_BL9 = QLabel("xx,xx (\u00B1 x,x %)")
        
        massestromGridLayout.addWidget(QLabel("BL9 (ZKMR zu)"), 0,0)
        massestromGridLayout.addWidget(QLabel("BL3 (ZKMR ab)"), 1,0)
        massestromGridLayout.addWidget(QLabel("BL1 (MH zu)"), 2,0)
        massestromGridLayout.addWidget(QLabel("BL7 (MH ab)"), 3,0)
        massestromGridLayout.addWidget(self.label_BL9, 0,1)
        massestromGridLayout.addWidget(self.label_BL3, 1,1)
        massestromGridLayout.addWidget(self.label_BL1, 2,1)
        massestromGridLayout.addWidget(self.label_BL7, 3,1)
        massestromGridLayout.addWidget(QLabel("kg/s"), 0,2)
        massestromGridLayout.addWidget(QLabel("kg/s"), 1,2)
        massestromGridLayout.addWidget(QLabel("kg/s"), 2,2)
        massestromGridLayout.addWidget(QLabel("kg/s"), 3,2)
        massestromGridLayout.setColumnStretch(0,3)
        massestromGridLayout.setColumnStretch(1,2)
        massestromGridLayout.setColumnStretch(2,1)
        self.button_ladeBlendenkonfig = QPushButton("lade Blendenkonfiguration", icon=QIcon(resource_path("res/Icon/folder_with_red_exclamationmark.ico")))
        self.button_ladeBlendenkonfig.clicked.connect(self.ladeBlendenkonf)

        self.label_Vordruck = QLabel("xx,xx")
        self.label_Filterdruck = QLabel("xx,xx")

        druckversorgungGridLayout.addWidget(QLabel("Vordruck"),    0,0)
        druckversorgungGridLayout.addWidget(QLabel("Filterdruck"), 1,0)
        druckversorgungGridLayout.addWidget(self.label_Vordruck   , 0,1)
        druckversorgungGridLayout.addWidget(self.label_Filterdruck, 1,1)
        druckversorgungGridLayout.addWidget(QLabel("bar"), 0,2)
        druckversorgungGridLayout.addWidget(QLabel("kPa"), 1,2)
        druckversorgungGridLayout.setColumnStretch(0,3)
        druckversorgungGridLayout.setColumnStretch(1,2)
        druckversorgungGridLayout.setColumnStretch(2,1)
        
        self.label_Telemetrie_A  = QLabel("xx,xx")
        self.label_Telemetrie_B  = QLabel("xx,xx")
        self.label_Telemetrie_IW = QLabel("xx,xx")

        betriebsspannungGridLayout.addWidget(QLabel("Telemetrie A"),  0,0)
        betriebsspannungGridLayout.addWidget(QLabel("Telemetrie B"),  1,0)
        betriebsspannungGridLayout.addWidget(QLabel("Telemetrie IW"), 2,0)
        betriebsspannungGridLayout.addWidget(self.label_Telemetrie_A,  0,1)
        betriebsspannungGridLayout.addWidget(self.label_Telemetrie_B,  1,1)
        betriebsspannungGridLayout.addWidget(self.label_Telemetrie_IW, 2,1)
        betriebsspannungGridLayout.addWidget(QLabel("V"), 0,2)
        betriebsspannungGridLayout.addWidget(QLabel("V"), 1,2)
        betriebsspannungGridLayout.addWidget(QLabel("V"), 2,2)
        betriebsspannungGridLayout.setColumnStretch(0,3)
        betriebsspannungGridLayout.setColumnStretch(1,2)
        betriebsspannungGridLayout.setColumnStretch(2,1)
        
        self.massFlowData =  {
           "BL1": { "uuid_p1": 0, "uuid_dp": 0, "uuid_T1": "", "D": 0, "d": 0, "dD": 0, "dd": 0, "dp1": 0, "ddp": 0, "dT1": 0},
           "BL3": { "uuid_p1": 0, "uuid_dp": 0, "uuid_T1": "", "D": 0, "d": 0, "dD": 0, "dd": 0, "dp1": 0, "ddp": 0, "dT1": 0},
           "BL7": { "uuid_p1": 0, "uuid_dp": 0, "uuid_T1": "", "D": 0, "d": 0, "dD": 0, "dd": 0, "dp1": 0, "ddp": 0, "dT1": 0},
           "BL9": { "uuid_p1": 0, "uuid_dp": 0, "uuid_T1": "", "D": 0, "d": 0, "dD": 0, "dd": 0, "dp1": 0, "ddp": 0, "dT1": 0}
        }

        self.dataLabels = [
            [self.label_Vordruck,       "G20-1_PAD_4"], 
            [self.label_Filterdruck,    "G20-1_PAD_3"], 
            [self.label_Telemetrie_A,   "Tele-A_PAD1"],
            [self.label_Telemetrie_B,   "Tele-B_PAD1"],
            [self.label_Telemetrie_IW,  "Tele-IW_PAD1"]
            ]

        self.fehlerLabel_A    = QLabel("x")
        self.fehlerLabel_B    = QLabel("x")
        self.fehlerLabel_IW   = QLabel("x")
        self.fehlerLabel_G201 = QLabel("x")
        self.fehlerLabel_G161 = QLabel("x")
        
        self.datensatzLabel_A    = QLabel("xxxx")
        self.datensatzLabel_B    = QLabel("xxxx")
        self.datensatzLabel_IW   = QLabel("xxxx")
        self.datensatzLabel_G201 = QLabel("xxxx")
        self.datensatzLabel_G161 = QLabel("xxxx")

        boltFont=QFont()
        boltFont.setBold(True)
        
        headerLabelList = ["Gerätename", "Datensatznr.", "Fehlerzähler"]
        
        self.fehlerLabelListe = [ 
            [self.fehlerLabel_A,    "Tele-A_Nummer"],
            [self.fehlerLabel_B,    "Tele-B_Nummer"],
            [self.fehlerLabel_IW,   "Tele-IW_Nummer"],
            [self.fehlerLabel_G201, "G20-1_Nummer"],
            [self.fehlerLabel_G161, "G16-1_Nummer"]
            ]
        
        self.datensatzLabelListe = [
            [self.datensatzLabel_A,    "Tele-A_Nummer"],
            [self.datensatzLabel_B,    "Tele-B_Nummer"],
            [self.datensatzLabel_IW,   "Tele-IW_Nummer"],
            [self.datensatzLabel_G201, "G20-1_Nummer"],
            [self.datensatzLabel_G161, "G16-1_Nummer"]
            ]
        
        for i in range(0, len(headerLabelList)):
            label = QLabel(headerLabelList[i])
            label.setFont(boltFont)
            fehlerGridLayout.addWidget(label, 0, i, alignment=Qt.AlignLeft)

        fehlerGridLayout.addWidget(QLabel("Telemetrie A"),   1, 0, alignment=Qt.AlignLeft)
        fehlerGridLayout.addWidget(QLabel("Telemetrie B"),   2, 0, alignment=Qt.AlignLeft)
        fehlerGridLayout.addWidget(QLabel("Telemetrie IW"),  3, 0, alignment=Qt.AlignLeft)
        fehlerGridLayout.addWidget(QLabel("Gerät G20.1"),    4, 0, alignment=Qt.AlignLeft)
        fehlerGridLayout.addWidget(QLabel("Gerät G16.1"),    5, 0, alignment=Qt.AlignLeft)
        fehlerGridLayout.addWidget(self.datensatzLabel_A,    1, 1, alignment=Qt.AlignRight)
        fehlerGridLayout.addWidget(self.datensatzLabel_B,    2, 1, alignment=Qt.AlignRight)
        fehlerGridLayout.addWidget(self.datensatzLabel_IW,   3, 1, alignment=Qt.AlignRight)
        fehlerGridLayout.addWidget(self.datensatzLabel_G201, 4, 1, alignment=Qt.AlignRight)
        fehlerGridLayout.addWidget(self.datensatzLabel_G161, 5, 1, alignment=Qt.AlignRight)
        fehlerGridLayout.addWidget(self.fehlerLabel_A,       1, 2, alignment=Qt.AlignRight)
        fehlerGridLayout.addWidget(self.fehlerLabel_B,       2, 2, alignment=Qt.AlignRight)
        fehlerGridLayout.addWidget(self.fehlerLabel_IW,      3, 2, alignment=Qt.AlignRight)
        fehlerGridLayout.addWidget(self.fehlerLabel_G201,    4, 2, alignment=Qt.AlignRight)
        fehlerGridLayout.addWidget(self.fehlerLabel_G161,    5, 2, alignment=Qt.AlignRight)
            

        massestromGroubox = QGroupBox("Massestrom")
        druckversorgungGroubox = QGroupBox("Druckversorgung")
        betriebsspannungGroupbox = QGroupBox("Betriebsspannung")
        fehlerGroubox = QGroupBox("Datenübertragung")

        massestromGroubox.setLayout(massestromGridLayout)
        druckversorgungGroubox.setLayout(druckversorgungGridLayout)
        betriebsspannungGroupbox.setLayout(betriebsspannungGridLayout)
        fehlerGroubox.setLayout(fehlerGridLayout)

        DruckBeriebsspannungLayout.addWidget(druckversorgungGroubox)
        DruckBeriebsspannungLayout.addWidget(betriebsspannungGroupbox)
        
        MassestromBlendenkonfigLayout.addWidget(massestromGroubox)
        MassestromBlendenkonfigLayout.addWidget(self.button_ladeBlendenkonfig)
        
        subLayout.addLayout(MassestromBlendenkonfigLayout)
        subLayout.addLayout(DruckBeriebsspannungLayout)
        subLayout.addWidget(fehlerGroubox)
        # subLayout.addStretch()
        massestromGroubox.setFixedHeight(160)
        druckversorgungGroubox.setFixedHeight(90)
        betriebsspannungGroupbox.setFixedHeight(120)
        fehlerGroubox.setFixedHeight(200)
        
        massestromGroubox.setFixedWidth(300)
        druckversorgungGroubox.setFixedWidth(300)
        betriebsspannungGroupbox.setFixedWidth(300)
        fehlerGroubox.setFixedWidth(300)
        
        mainLayout.addWidget(msWidget)
        mainLayout.addLayout(subLayout)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        msWidget.setFixedSize(920,660)
        backgroundLabel = QLabel(msWidget)
        offset_x = 60
        offset_y = 80
        backgroundLabel.move(offset_x, offset_y)
        backgroundLabel.setScaledContents(True)
        b = 800
        h = 600
        backgroundLabel.setFixedSize(b,h)
        pixmap = QPixmap(str(Path('res/Pictures/Betriebsmesstechnik_Messstellen.png')))
        backgroundLabel.setPixmap(pixmap)
        
        def x(x_rel):
            return int((offset_x+b)*x_rel)
        
        def y(y_rel):
            return int((offset_y+h)*y_rel)

        offsetButton = QPushButton("Set Offset", msWidget)
        offsetButton.move(x(0.965), y(0.050))
        offsetButton.clicked.connect(self.setOffsetFlag)
        
        resetOffsetButton = QPushButton("Toggle Offset", msWidget)
        resetOffsetButton.move(x(0.850), y(0.050))
        resetOffsetButton.clicked.connect(self.toggleOffset)

        self.graphicalMeasurements = []
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.000), y(0.120), "G20-1_SPI1_5",  "TLRT",   "°C",   "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.000), y(0.250), "G20-1_SPI2_0",  "TLSBL9", "°C",   "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.000), y(0.325), "G20-1_A10",     "DDSBL9", "Pa",   "DD"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.000), y(0.400), "G20-1_A9",      "DSBL9",  "Pa",   "DA"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.000), y(0.490), "G20-1_SPI1_3",  "TLSA",   "°C",   "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.000), y(0.620), "G16-1_PC3_1",   "DSA",    "Pa",   "DA"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.190), y(0.700), "G20-1_Periode_0", "RPM",  "rpm",  "RPM"))
        # self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.190), y(0.250), "G20-1_SPI1_1",  "TSA2",   "°C",   "TE")) # Vorerst irrelevant
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.190), y(0.250), "Tele-A_PM1_6",  "T Tele-A",   "°C",   "TE")) 
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.190), y(0.325), "G20-1_SPI1_0",  "TSA1",   "°C",   "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.190), y(0.400), "G16-1_SPI_6",   "SWA",    "mm/s", "SWS"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.290), y(0.250), "G16-1_SPI_2",   "LTKR",   "°C",   "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.290), y(0.325), "G16-1_SPI_0",   "GTARA2", "°C",   "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.290), y(0.400), "G16-1_SPI_1",   "GTMRaA", "°C",   "TE"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.610), y(0.025), "G20-1_SPI2_3",  "TLSBL7", "°C",   "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.610), y(0.100), "G20-1_B4",      "DDSBL7", "Pa",   "DD"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.610), y(0.175), "G20-1_B3",      "DSBL7",  "Pa",   "DA"))
        
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.370), y(0.025), "G20-1_SPI2_1",  "TLSBL1", "°C",   "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.370), y(0.100), "G20-1_A2",      "DDSBL1", "Pa",   "DD"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.370), y(0.175), "G20-1_A1",      "DSBL1",  "Pa",   "DA"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.683), y(0.250), "G16-1_PC3_2",   "LPKR",   "Pa",   "DA"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.683), y(0.325), "G16-1_SPI_4",   "GTARB2", "°C",   "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.683), y(0.400), "G16-1_SPI_3",   "GTMRaB", "°C",   "TE"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.783), y(0.250), "Tele-B_PM1_6",  "T Tele-B",   "°C",   "TE")) 
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.783), y(0.325), "G20-1_SPI1_2",  "TSB1",   "°C",   "TE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.783), y(0.400), "G16-1_SPI_7",   "SWB",    "mm/s", "SWS"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.800), y(0.710), "G16-1_SPI_5",   "TOelZu", "°C",   "LTE"))

        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.950), y(0.250), "G20-1_SPI2_2",  "TLSBL3", "°C",   "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.950), y(0.325), "G20-1_A6",      "DDSBL3", "Pa",   "DD"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.950), y(0.400), "G20-1_A5",      "DSBL3",  "Pa",   "DA"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.950), y(0.490), "G20-1_SPI1_4",  "TLSB",   "°C",   "LTE"))
        self.graphicalMeasurements.append(GraphicalMeasurement(msWidget, x(0.950), y(0.620), "G16-1_PC3_0",   "DSB",    "Pa",   "DA"))

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        resetOffsetFlag = False
        
        for graphicalMeasurement in self.graphicalMeasurements:
            vData = self.findCalibratedDataByUUID(data, dataInfo, graphicalMeasurement.uuid)
            
            if vData is not None:
                if graphicalMeasurement.uuid in ["G20-1_A2", "G20-1_A6", "G20-1_B4", "G20-1_A10"]:
                    if self.offsetFlag == True:
                        resetOffsetFlag = True
                        self.setGlobalVarsEntry(graphicalMeasurement.uuid, vData) 
                    if self.useOffset:
                        if graphicalMeasurement.uuid in self.getGlobalVars().keys():
                            graphicalMeasurement.setValueText(str("{0:6.1f}").format(vData-self.getGlobalVarsEntry(graphicalMeasurement.uuid))) 
                        else:
                            graphicalMeasurement.setValueText(str("{0:6.1f}").format(vData))
                            # print("{0:} not found in global variables list!".format(graphicalMeasurement.uuid))
                    else:
                        graphicalMeasurement.setValueText(str("{0:6.1f}").format(vData))
                else:
                    graphicalMeasurement.setValueText(str("{0:6.1f}").format(vData))
                
        for label in self.dataLabels:
            vData = self.findCalibratedDataByUUID(data, dataInfo, label[1])
            if vData is not None:
                if label[1] == "G20-1_PAD_3":
                    if self.offsetFlag == True:
                        self.setGlobalVarsEntry("G20-1_PAD_3", vData) 
                    if self.useOffset:
                        if "G20-1_PAD_3" in self.getGlobalVars().keys():
                            label[0].setText(str("{0:10.2f}").format(vData-self.getGlobalVarsEntry("G20-1_PAD_3")))
                        else:
                            label[0].setText(str("{0:10.2f}").format(vData))
                            # print("G20-1_PAD_3 not found in global variables list!")
                    else:
                        label[0].setText(str("{0:10.2f}").format(vData))
                else:
                    label[0].setText(str("{0:10.2f}").format(vData)) 
        
        for key in self.massFlowData:
            p1  = self.findCalibratedDataByUUID(data, dataInfo, self.massFlowData[key]["uuid_p1"])
            dp  = self.findCalibratedDataByUUID(data, dataInfo, self.massFlowData[key]["uuid_dp"])
            T1  = self.findCalibratedDataByUUID(data, dataInfo, self.massFlowData[key]["uuid_T1"])
            
            if key  == "BL1":
                massFlowLabel = self.label_BL1
            elif  key  == "BL3":
                massFlowLabel = self.label_BL3
            elif  key  == "BL7":
                massFlowLabel = self.label_BL7
            elif  key  == "BL9":
                massFlowLabel = self.label_BL9
            
            if self.useOffset and dp is not None:
                if "G20-1_A10" in self.getGlobalVars().keys():
                    dp -= self.getGlobalVarsEntry(self.massFlowData[key]["uuid_dp"])
                # else:
                #     print("G20-1_A10 not found in global variables list!")
            
            D   = self.massFlowData[key]["D"]
            d   = self.massFlowData[key]["d"]
            dD  = self.massFlowData[key]["dD"]
            dd  = self.massFlowData[key]["dd"]
            dp1 = self.massFlowData[key]["dp1"]
            ddp = self.massFlowData[key]["ddp"]
            dT1 = self.massFlowData[key]["dT1"]

            if (p1 is not None) and (dp is not None) and (T1 is not None):
                blende = Blendenmessung(D, d, p1, dp, T1+273.15, dp1=dp1, ddp=ddp, dT1=dT1, dD=dD, dd=dd)
                blende.Massestrom()
                blende.Fehlerrechnung()
                vData = blende.qm
                wData = blende.dqmp
                massFlowLabel.setText(str("{0:1.3f} (\u00B1 {1:2.2f} %)").format(vData, wData))
        
        for label in self.fehlerLabelListe:  
            errorCounter = serialParameters.errorCounter
            testData = self.findCalibratedDataByUUID(data, dataInfo, label[1])
            if testData is not None:
                label[0].setText(str("{0:}").format(errorCounter))

        for label in self.datensatzLabelListe:
            vData = self.findCalibratedDataByUUID(data, dataInfo, label[1])
            if vData is not None:
                label[0].setText(str("{0:}").format(vData))

        if resetOffsetFlag == True:
            self.offsetFlag = False


    def setOffsetFlag(self):
        self.offsetFlag = True
        
        
    def toggleOffset(self):

        if self.useOffset:
            self.useOffset = False
        else:
            self.useOffset =True


    def sendData(self):
        # self.sendSerialData() ist eine interne Funktion, die die activen Ports berücksichtigt
        self.sendSerialData("sending test data...")


    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        return ""


    def load(self, data):
        pass
    
    
    def globalVarsChanged(self, id: str):
        
        for elem in ["BL1", "BL3", "BL7", "BL9"]:
            if elem in self.getGlobalVars().keys():
                for key in self.massFlowData[elem]:
                    self.massFlowData[elem][key] = self.getGlobalVars()[elem][key]


    def ladeBlendenkonf(self):
        
        filePaths, filter = QFileDialog.getOpenFileNames(self, 'Open orifice disk parameter from file', "", "*.json", "", QFileDialog.DontUseNativeDialog) 

        for filePath in filePaths:
            if filePath != '' and os.path.isfile(filePath):
                
                with open(filePath, "r") as file:
                    raw_data = file.read()
                    try:
                        if sys.version_info >= (3, 9):
                            data = json.loads(raw_data)
                        else:
                            data = json.loads(raw_data, encoding='utf-8')

                        if self.gueltigeBlendendaten(data):
                            for elem in data:
                                self.setGlobalVarsEntry(elem, data[elem])
                            self.button_ladeBlendenkonfig.setIcon(QIcon(resource_path("res/Icon/folder_with_green_checkmark.ico")))
                        else:
                            self.button_ladeBlendenkonfig.setIcon(QIcon(resource_path("res/Icon/folder_with_red_exclamationmark.ico")))
                            print("Ungültige Blendendaten!")
        
                    except json.JSONDecodeError:
                        raise TypeError("%s is not a valid JSON file" % os.path.basename(filePath))
                    except Exception as e:
                        print(e)    
            else:
                print("File not existing!")
                
    
    def gueltigeBlendendaten(self, data):
        
        if type(data) == dict:
            if  "BL1" in data.keys() and  "BL3" in data.keys() and  "BL7" in data.keys() and  "BL9" in data.keys():
                ref = sorted(["uuid_p1", "uuid_dp", "uuid_T1", "D", "d", "dD", "dd", "dp1", "ddp", "dT1"])
                if ref == sorted(data["BL1"].keys()) and ref == sorted(data["BL3"].keys()) and ref == sorted(data["BL7"].keys()) and ref == sorted(data["BL9"].keys()):
                    return True
                else:
                    print("Orifice disk parameters not set correctly!")
                    return False
            else:
                print("Not all orifice disk parameters set!")
                return False  
        else:
            print("Not a dictionary!")
            return False  