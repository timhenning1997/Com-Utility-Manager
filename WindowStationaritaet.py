from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QDoubleSpinBox
from PyQt5.QtGui import QColor
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from Blendenmessung import Blendenmessung
import numpy as np
import time

class WindowStationaritaet(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "Stationaritaet")
        
        self.staParam = {   # diff = Max-Min, grad = Grad/h
            "Mantel_T":     {"diff": 2.0e+0, "grad": 1.0e+0}, # °C
            "Drehzahl":     {"diff": 2.0e+0, "grad": 1.0e+0}, # 1/min
            "Druck":        {"diff": 2.0e+3, "grad": 1.0e+3}, # Pa
            "Massestrom":   {"diff": 2.0e-3, "grad": 1.0e-3}, # kg/s
            "Zuluft_T":     {"diff": 2.0e+0, "grad": 1.0e+0}  # °C
        }
        
        rowNames = ["Mantel T", "Drehzahl", "Druck", "Massestrom", "Zuluft T"]
        columnNames = ["Mittelwert", "Max-Min", "Gradient", "Zeitpuffer", "Stationarität"]
        
        rows = len(rowNames)
        columns = len(columnNames)
        
        self.datatable = QTableWidget(rows, columns)
        self.datatable.setHorizontalHeaderLabels(columnNames)
        self.datatable.setVerticalHeaderLabels(rowNames)
        
        for x in range(0, columns):
            self.datatable.horizontalHeader().setSectionResizeMode(x, QHeaderView.Stretch)
        for x in range(0, rows): 
            self.datatable.verticalHeader().setSectionResizeMode(x, QHeaderView.Stretch)
        
        for x in range(0,rows):
            for y in range(0,columns):
                nameWidget = QTableWidgetItem()
                self.datatable.setItem(x, y, nameWidget)
        
        self.label_Messdauer = QLabel("Messdauer")
        self.doublespinbox_Messdauer = QDoubleSpinBox()
        self.doublespinbox_Messdauer.setRange(0.1, 999)
        self.doublespinbox_Messdauer.setValue(30)
        self.doublespinbox_Messdauer.setAlignment(Qt.AlignRight)
        self.doublespinbox_Messdauer.setSuffix(" Minuten")
        self.doublespinbox_Messdauer.setDecimals(1)
        self.doublespinbox_Messdauer.editingFinished.connect(self.setzeMessdauer)
        
        subLayout1 = QGridLayout()
        subLayout1.addWidget(self.label_Messdauer,0,0)
        subLayout1.addWidget(self.doublespinbox_Messdauer,0,1)   
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.datatable)
        mainLayout.addLayout(subLayout1)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
        self.resize(600, 240)
        
        self.setzeMessdauer()
        
        self.MantelT    = []
        self.Drehzahl   = []
        self.Druck      = []
        self.Massestrom = []
        self.ZuluftT    = []
    
        self.MantelT_time    = []
        self.Drehzahl_time   = []
        self.Druck_time      = []
        self.Massestrom_time = []
        self.ZuluftT_time    = []
        
        self.MantelT_anzahlEmpfangenerDaten    = 0
        self.Drehzahl_anzahlEmpfangenerDaten   = 0
        self.Druck_anzahlEmpfangenerDaten      = 0
        self.Massestrom_anzahlEmpfangenerDaten = 0
        self.ZuluftT_anzahlEmpfangenerDaten    = 0
        
        self.D = 0
        self.d = 0
        

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        
        TM29    = self.findCalibratedDataByUUID(data, dataInfo, "Tele-B_PAD7_0") # TM29
        TM34    = self.findCalibratedDataByUUID(data, dataInfo, "Tele-B_PAD7_5") # TM34
        TM35    = self.findCalibratedDataByUUID(data, dataInfo, "Tele-B_PAD7_6") # TM35
        TM40    = self.findCalibratedDataByUUID(data, dataInfo, "Tele-B_PAD6_4") # TM40
        RPM     = self.findCalibratedDataByUUID(data, dataInfo, "G16-1_Periode_0") # RPM
        DSA     = self.findCalibratedDataByUUID(data, dataInfo, "G16-1_PC3_1") # DSA
        DSBL9   = self.findCalibratedDataByUUID(data, dataInfo, "G20-1_A9") # DSBL9
        DdSBL9  = self.findCalibratedDataByUUID(data, dataInfo, "G20-1_A10") # DdSBL9
        TLSBL9  = self.findCalibratedDataByUUID(data, dataInfo, "G20-1_SPI2_0") # TLSBL9
        TLSA    = self.findCalibratedDataByUUID(data, dataInfo, "G20-1_SPI1_3") # TLSA
        
        zeit   = time.time()
        
        if (TM29 is not None) and (TM34 is not None) and (TM35 is not None) and (TM40 is not None):
            
            self.MantelT_anzahlEmpfangenerDaten    += 1
            self.MantelT.append((TM29 + TM34 + TM35 + TM40)/4)
            self.MantelT_time.append(zeit)
            
            if self.MantelT_anzahlEmpfangenerDaten % 10 == 0 and self.MantelT_anzahlEmpfangenerDaten > 5:
                
                x       = (np.array(self.MantelT_time) - self.MantelT_time[0]) / 3600
                grad    = np.polyfit(x, self.MantelT, 1)[0]
                diff    = max(self.MantelT)- min(self.MantelT)
                puffer  = min(100, (self.MantelT_time[-1] - self.MantelT_time[0]) / self.zeitraum * 100)
                
                if grad <= self.staParam["Mantel_T"]["grad"] and diff <= self.staParam["Mantel_T"]["diff"] and puffer >= 100.0:
                    stat = True
                    self.datatable.item(0,4).setBackground(QColor(63, 174, 9))
                else:
                    stat = False
                    self.datatable.item(0,4).setBackground(QColor(255, 128, 128))
            
                self.datatable.item(0, 0).setText("{0:12.2f} °C".format(np.mean(self.MantelT)))
                self.datatable.item(0, 1).setText("{0:12.2f} °C".format(diff))
                self.datatable.item(0, 2).setText("{0:12.2f} °C/h".format(grad)) 
                self.datatable.item(0, 3).setText("{0:8.2f} %".format(puffer))
                self.datatable.item(0, 4).setText("{0:}".format(stat)) 
                
                self.MantelT_anzahlEmpfangenerDaten = 0
                
            while (self.MantelT_time[-1] - self.MantelT_time[0] > self.zeitraum + 1):
                self.MantelT = self.MantelT[1:]
                self.MantelT_time = self.MantelT_time[1:]
            
        if RPM is not None:
            
            self.Drehzahl_anzahlEmpfangenerDaten   += 1
            self.Drehzahl.append(RPM)
            self.Drehzahl_time.append(zeit)
            
            if self.Drehzahl_anzahlEmpfangenerDaten % 10 == 0 and self.Drehzahl_anzahlEmpfangenerDaten > 5:
                
                x       = (np.array(self.Drehzahl_time) - self.Drehzahl_time[0]) / 3600
                grad    = np.polyfit(x, self.Drehzahl, 1)[0]
                diff    = max(self.Drehzahl)- min(self.Drehzahl)
                puffer  = min(100, (self.Drehzahl_time[-1] - self.Drehzahl_time[0]) / self.zeitraum * 100)
                
                if grad <= self.staParam["Drehzahl"]["grad"] and diff <= self.staParam["Drehzahl"]["diff"] and puffer >= 100.0:
                    stat = True
                    self.datatable.item(1,4).setBackground(QColor(63, 174, 9))
                else:
                    stat = False
                    self.datatable.item(1,4).setBackground(QColor(255, 128, 128))
            
                self.datatable.item(1, 0).setText("{0:12.0f} rpm".format(np.mean(self.Drehzahl)))
                self.datatable.item(1, 1).setText("{0:12.0f} rpm".format(diff))
                self.datatable.item(1, 2).setText("{0:12.0f} rpm/h".format(grad)) 
                self.datatable.item(1, 3).setText("{0:8.2f} %".format(puffer))
                self.datatable.item(1, 4).setText("{0:}".format(stat)) 
                
                self.Drehzahl_anzahlEmpfangenerDaten = 0
                
            while (self.Drehzahl_time[-1] - self.Drehzahl_time[0] > self.zeitraum + 1):
                self.Drehzahl = self.Drehzahl[1:]
                self.Drehzahl_time = self.Drehzahl_time[1:]
            
        if DSA is not None:
            
            self.Druck_anzahlEmpfangenerDaten      += 1
            self.Druck.append(DSA)
            self.Druck_time.append(zeit)
            
            if self.Druck_anzahlEmpfangenerDaten % 10 == 0 and self.Druck_anzahlEmpfangenerDaten > 5:
                
                x       = (np.array(self.Druck_time) - self.Druck_time[0]) / 3600
                grad    = np.polyfit(x, self.Druck, 1)[0]
                diff    = max(self.Druck)- min(self.Druck)
                puffer  = min(100, (self.Druck_time[-1] - self.Druck_time[0]) / self.zeitraum * 100)
                
                if grad <= self.staParam["Druck"]["grad"] and diff <= self.staParam["Druck"]["diff"] and puffer >= 100.0:
                    stat = True
                    self.datatable.item(2,4).setBackground(QColor(63, 174, 9))
                else:
                    stat = False
                    self.datatable.item(2,4).setBackground(QColor(255, 128, 128))
            
                self.datatable.item(2, 0).setText("{0:12.0f} Pa".format(np.mean(self.Druck)))
                self.datatable.item(2, 1).setText("{0:12.0f} Pa".format(diff))
                self.datatable.item(2, 2).setText("{0:12.0f} Pa/h".format(grad)) 
                self.datatable.item(2, 3).setText("{0:8.2f} %".format(puffer))
                self.datatable.item(2, 4).setText("{0:}".format(stat)) 
                
                self.Druck_anzahlEmpfangenerDaten = 0
                
            while (self.Druck_time[-1] - self.Druck_time[0] > self.zeitraum + 1):
                self.Druck = self.Druck[1:]
                self.Druck_time = self.Druck_time[1:]
            
        if (DSBL9 is not None) and (DdSBL9 is not None) and (TLSBL9 is not None):
            
            self.Massestrom_anzahlEmpfangenerDaten += 1
            blende = Blendenmessung(self.D, self.d, DSBL9, DdSBL9, TLSBL9+273.15)
            blende.Massestrom()
            self.Massestrom.append(blende.qm)
            self.Massestrom_time.append(zeit)
            
            if self.Massestrom_anzahlEmpfangenerDaten % 10 == 0 and self.Massestrom_anzahlEmpfangenerDaten > 5:
                
                x       = (np.array(self.Massestrom_time) - self.Massestrom_time[0]) / 3600
                grad    = np.polyfit(x, self.Massestrom, 1)[0]
                diff    = max(self.Massestrom)- min(self.Massestrom)
                puffer  = min(100, (self.Massestrom_time[-1] - self.Massestrom_time[0]) / self.zeitraum * 100)
                
                if grad <= self.staParam["Massestrom"]["grad"] and diff <= self.staParam["Massestrom"]["diff"] and puffer >= 100.0:
                    stat = True
                    self.datatable.item(3,4).setBackground(QColor(63, 174, 9))
                else:
                    stat = False
                    self.datatable.item(3,4).setBackground(QColor(255, 128, 128))
            
                self.datatable.item(3, 0).setText("{0:12.4f} kg/s".format(np.mean(self.Massestrom)))
                self.datatable.item(3, 1).setText("{0:12.4f} kg/s".format(diff))
                self.datatable.item(3, 2).setText("{0:12.2f} kg/s / h".format(grad)) 
                self.datatable.item(3, 3).setText("{0: 8.2f} %".format(puffer))
                self.datatable.item(3, 4).setText("{0:}".format(stat)) 
                
                self.Massestrom_anzahlEmpfangenerDaten = 0
                
            while (self.Massestrom_time[-1] - self.Massestrom_time[0] > self.zeitraum + 1):
                self.Massestrom = self.Massestrom[1:]
                self.Massestrom_time = self.Massestrom_time[1:]
            
        if TLSA is not None:
            
            self.ZuluftT_anzahlEmpfangenerDaten    += 1
            self.ZuluftT.append(TLSA)
            self.ZuluftT_time.append(zeit)
            
            if self.ZuluftT_anzahlEmpfangenerDaten % 10 == 0 and self.ZuluftT_anzahlEmpfangenerDaten > 5:
                
                x       = (np.array(self.ZuluftT_time) - self.ZuluftT_time[0]) / 3600
                grad    = np.polyfit(x, self.ZuluftT, 1)[0]
                diff    = max(self.ZuluftT)- min(self.ZuluftT)
                puffer  = min(100, (self.ZuluftT_time[-1] - self.ZuluftT_time[0]) / self.zeitraum * 100)
                
                if grad <= self.staParam["Zuluft_T"]["grad"] and diff <= self.staParam["Zuluft_T"]["diff"] and puffer >= 100.0:
                    stat = True
                    self.datatable.item(4,4).setBackground(QColor(63, 174, 9))
                else:
                    stat = False
                    self.datatable.item(4,4).setBackground(QColor(255, 128, 128))
            
                self.datatable.item(4, 0).setText("{0:12.2f} °C".format(np.mean(self.ZuluftT)))
                self.datatable.item(4, 1).setText("{0:12.2f} °C".format(diff))
                self.datatable.item(4, 2).setText("{0:12.2f} °C/h".format(grad)) 
                self.datatable.item(4, 3).setText("{0:8.2f} %".format(puffer))
                self.datatable.item(4, 4).setText("{0:}".format(stat)) 
                
                self.ZuluftT_anzahlEmpfangenerDaten = 0
                
            while (self.ZuluftT_time[-1] - self.ZuluftT_time[0] > self.zeitraum + 1):
                self.ZuluftT = self.ZuluftT[1:]
                self.ZuluftT_time = self.ZuluftT_time[1:]

    def setzeMessdauer(self):
        
        if self.doublespinbox_Messdauer.text() in ["", "0", "0.", ".", ".01"]:
            self.zeitraum = 30*60
        else:
            self.zeitraum = self.doublespinbox_Messdauer.value()*60

    def sendData(self):
        pass

    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        return ""

    def load(self, data):
        pass
    
    def globalVarsChanged(self, id: str):
        
        for elem in ["BL9"]:
            if elem in self.getGlobalVars().keys():
                self.D = self.getGlobalVarsEntry("BL9")["D"]
                self.d = self.getGlobalVarsEntry("BL9")["d"]
