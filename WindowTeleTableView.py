from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QPixmap, QFont
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters

class WindowTeleTableView(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "TeleTableView")
        
        # Dem Hauptfenster ein Layout zuweisen
        scheibeALayout = QVBoxLayout()
        scheibeBLayout = QVBoxLayout()
        scheibeMLayout = QVBoxLayout()
        scheibeMMantelLayout = QVBoxLayout()
        innenwelleLayout = QVBoxLayout()
        
        mainLayout = QHBoxLayout()
        
        mainLayout.addLayout(scheibeALayout)
        mainLayout.addLayout(scheibeBLayout)
        mainLayout.addLayout(scheibeMLayout)
        mainLayout.addLayout(scheibeMMantelLayout)
        mainLayout.addLayout(innenwelleLayout)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
        
        self.scheibeATableTE = QTableWidget(26, 3)
        self.scheibeBTableTE = QTableWidget(26, 3)
        self.scheibeMTableTE = QTableWidget(28, 3)
        self.scheibeMMantelTableTE = QTableWidget(28, 3)
        self.innenwelleTableTE = QTableWidget(3, 3)
        
        self.scheibeATableDA = QTableWidget(8, 3)
        self.scheibeBTableDA = QTableWidget(8, 3)
        
        self.innenwelleTableLTE = QTableWidget(9, 3)
        self.scheibeATableLTE = QTableWidget(6, 3)
        self.scheibeMTableLTE = QTableWidget(6, 3)
        
        tables = [self.scheibeATableTE, self.scheibeBTableTE, self.scheibeMTableTE, self.scheibeMMantelTableTE, self.innenwelleTableTE, self.scheibeATableDA, self.scheibeBTableDA, self.innenwelleTableLTE, self.scheibeATableLTE, self.scheibeMTableLTE]
        
        for table in tables:
            table.setHorizontalHeaderLabels(["Name", "Wert", "E"])
            # for column in range(0, table.columnCount()):
            #     table.horizontalHeader().setSectionResizeMode(column, QHeaderView.Stretch)

            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
            table.setColumnWidth(0, 50)
            table.setColumnWidth(1, 50)
            table.setColumnWidth(2, 30)
            
            rowHeight = 10
            for row in range(0, table.rowCount()):
                table.setRowHeight(row, rowHeight)
                table.verticalHeader().setSectionResizeMode(row, QHeaderView.Stretch)

        
        
        label_A = QLabel(" Scheibe A")
        label_A.setStyleSheet("font: 14pt; color : white;")
        scheibeALayout.addWidget(label_A)
        label_TE = QLabel(" Thermoelemente")
        label_TE.setStyleSheet("background-color: #FFA99B; color : black; font: 12pt;") 
        scheibeALayout.addWidget(label_TE)
        scheibeALayout.addWidget(self.scheibeATableTE, stretch=26)
        label_DA = QLabel(" Absolutdrucksensoren")
        label_DA.setStyleSheet("background-color: #FFF2CC; color : black; font: 12pt")
        scheibeALayout.addWidget(label_DA)
        scheibeALayout.addWidget(self.scheibeATableDA, stretch=8)

        label_B = QLabel(" Scheibe B")
        label_B.setStyleSheet("font: 14pt; color : white;")   
        scheibeBLayout.addWidget(label_B)
        label_TE = QLabel(" Thermoelemente")
        label_TE.setStyleSheet("background-color: #FFA99B; color : black; font: 12pt;") 
        scheibeBLayout.addWidget(label_TE)
        scheibeBLayout.addWidget(self.scheibeBTableTE, stretch=26)
        label_DA = QLabel(" Absolutdrucksensoren")
        label_DA.setStyleSheet("background-color: #FFF2CC; color : black; font: 12pt")
        scheibeBLayout.addWidget(label_DA)
        scheibeBLayout.addWidget(self.scheibeBTableDA, stretch=8)

        label_M = QLabel(" Scheibe M")
        label_M.setStyleSheet("font: 14pt; color : white;") 
        scheibeMLayout.addWidget(label_M)
        label_TE = QLabel(" Thermoelemente")
        label_TE.setStyleSheet("background-color: #FFA99B; color : black; font: 12pt;") 
        scheibeMLayout.addWidget(label_TE)
        scheibeMLayout.addWidget(self.scheibeMTableTE, stretch=28)

        label_Mm = QLabel(" Scheibe Mantel M")
        label_Mm.setStyleSheet("font: 14pt; color : white;") 
        scheibeMMantelLayout.addWidget(label_Mm)
        label_TE = QLabel(" Thermoelemente")
        label_TE.setStyleSheet("background-color: #FFA99B; color : black; font: 12pt;") 
        scheibeMMantelLayout.addWidget(label_TE)
        scheibeMMantelLayout.addWidget(self.scheibeMMantelTableTE, stretch=28)

        label_IW = QLabel(" Innenwelle")
        label_IW.setStyleSheet("font: 14pt; color : white;") 
        innenwelleLayout.addWidget(label_IW)
        label_TE = QLabel(" Thermoelemente")
        label_TE.setStyleSheet("background-color: #FFA99B; color : black; font: 12pt;") 
        innenwelleLayout.addWidget(label_TE)
        innenwelleLayout.addWidget(self.innenwelleTableTE, stretch=3)
        label_LTE = QLabel(" Luft-Thermoelemente")
        label_LTE.setStyleSheet("background-color: #BDD7EE; color : black; font: 12pt")
        innenwelleLayout.addWidget(label_LTE)
        innenwelleLayout.addWidget(self.innenwelleTableLTE, stretch=9)
        label_A = QLabel(" Scheibe A")
        label_A.setStyleSheet("font: 14pt; color : white;")
        innenwelleLayout.addWidget(label_A)
        label_LTE = QLabel(" Luft-Thermoelemente")
        label_LTE.setStyleSheet("background-color: #BDD7EE; color : black; font: 12pt")
        innenwelleLayout.addWidget(label_LTE)
        innenwelleLayout.addWidget(self.scheibeATableLTE, stretch=6)
        label_M = QLabel(" Scheibe M")
        label_M.setStyleSheet("font: 14pt; color : white;") 
        innenwelleLayout.addWidget(label_M)
        label_LTE = QLabel(" Luft-Thermoelemente")
        label_LTE.setStyleSheet("background-color: #BDD7EE; color : black; font: 12pt")
        innenwelleLayout.addWidget(label_LTE)
        innenwelleLayout.addWidget(self.scheibeMTableLTE, stretch=6)
        
        for i in range (0, self.scheibeATableTE.rowCount()):
            self.scheibeATableTE.setItem(i, 1, QTableWidgetItem())
            self.scheibeATableTE.item(i, 1).setTextAlignment(Qt.AlignRight)
        
        
        self.list_A_TA = [
            {"name": "TA1", "UUID":  "EcoFlex-TeleA_PP0_0", "unit": "°C"}, 
            {"name": "TA2", "UUID":  "EcoFlex-TeleA_PP0_1", "unit": "°C"},
            {"name": "TA3", "UUID":  "EcoFlex-TeleA_PP0_2", "unit": "°C"},
            {"name": "TA4", "UUID":  "EcoFlex-TeleA_PP0_3", "unit": "°C"},
            {"name": "TA5", "UUID":  "EcoFlex-TeleA_PP0_4", "unit": "°C"},
            {"name": "TA6", "UUID":  "EcoFlex-TeleA_PP0_5", "unit": "°C"},
            {"name": "TA7", "UUID":  "EcoFlex-TeleA_PP1_0", "unit": "°C"},
            {"name": "TA8", "UUID":  "EcoFlex-TeleA_PP1_1", "unit": "°C"},
            {"name": "TA9", "UUID":  "EcoFlex-TeleA_PP1_2", "unit": "°C"},
            {"name": "TA10", "UUID": "EcoFlex-TeleA_PP1_3", "unit": "°C"},
            {"name": "TA11", "UUID": "EcoFlex-TeleA_PP1_4", "unit": "°C"},
            {"name": "TA12", "UUID": "EcoFlex-TeleA_PP1_5", "unit": "°C"},
            {"name": "TA13", "UUID": "EcoFlex-TeleA_PP2_0", "unit": "°C"},
            {"name": "TA14", "UUID": "EcoFlex-TeleA_PP2_1", "unit": "°C"},
            {"name": "TA15", "UUID": "EcoFlex-TeleA_PP2_2", "unit": "°C"},
            {"name": "TA16", "UUID": "EcoFlex-TeleA_PP2_3", "unit": "°C"},
            {"name": "TA17", "UUID": "EcoFlex-TeleA_PP2_4", "unit": "°C"},
            {"name": "TA18", "UUID": "EcoFlex-TeleA_PP2_5", "unit": "°C"},
            {"name": "TA19", "UUID": "EcoFlex-TeleA_PP2_6", "unit": "°C"},
            {"name": "TA20", "UUID": "EcoFlex-TeleA_PP3_0", "unit": "°C"},
            {"name": "TA21", "UUID": "EcoFlex-TeleA_PP3_1", "unit": "°C"},
            {"name": "TA22", "UUID": "EcoFlex-TeleA_PP3_2", "unit": "°C"},
            {"name": "TA23", "UUID": "EcoFlex-TeleA_PP3_3", "unit": "°C"},
            {"name": "TA24", "UUID": "EcoFlex-TeleA_PP3_4", "unit": "°C"},
            {"name": "TA25", "UUID": "EcoFlex-TeleA_PP3_5", "unit": "°C"},
            {"name": "TA26", "UUID": "EcoFlex-TeleA_PP3_6", "unit": "°C"}]
        
        self.list_A_DA = [
            {"name": "DA1", "UUID": "EcoFlex-TeleA_PM0_0", "unit": "Pa"},
            {"name": "DA2", "UUID": "EcoFlex-TeleA_PM0_1", "unit": "Pa"},
            {"name": "DA3", "UUID": "EcoFlex-TeleA_PM0_2", "unit": "Pa"},
            {"name": "DA4", "UUID": "EcoFlex-TeleA_PM0_3", "unit": "Pa"},
            {"name": "DA5", "UUID": "EcoFlex-TeleA_PM0_4", "unit": "Pa"},
            {"name": "DA6", "UUID": "EcoFlex-TeleA_PM0_5", "unit": "Pa"},
            {"name": "DA7", "UUID": "EcoFlex-TeleA_PM0_6", "unit": "Pa"},
            {"name": "DA8", "UUID": "EcoFlex-TeleA_PM0_7", "unit": "Pa"}]
        
        self.list_B_TE = [
            {"name": "TB1", "UUID":  "EcoFlex-TeleB_PP0_0", "unit": "°C"}, 
            {"name": "TB2", "UUID":  "EcoFlex-TeleB_PP0_1", "unit": "°C"},
            {"name": "TB3", "UUID":  "EcoFlex-TeleB_PP0_2", "unit": "°C"},
            {"name": "TB4", "UUID":  "EcoFlex-TeleB_PP0_3", "unit": "°C"},
            {"name": "TB5", "UUID":  "EcoFlex-TeleB_PP0_4", "unit": "°C"},
            {"name": "TB6", "UUID":  "EcoFlex-TeleB_PP0_5", "unit": "°C"},
            {"name": "TB7", "UUID":  "EcoFlex-TeleB_PP1_0", "unit": "°C"},
            {"name": "TB8", "UUID":  "EcoFlex-TeleB_PP1_1", "unit": "°C"},
            {"name": "TB9", "UUID":  "EcoFlex-TeleB_PP1_2", "unit": "°C"},
            {"name": "TB10", "UUID": "EcoFlex-TeleB_PP1_3", "unit": "°C"},
            {"name": "TB11", "UUID": "EcoFlex-TeleB_PP1_4", "unit": "°C"},
            {"name": "TB12", "UUID": "EcoFlex-TeleB_PP1_5", "unit": "°C"},
            {"name": "TB13", "UUID": "EcoFlex-TeleB_PT3_0", "unit": "°C"},
            {"name": "TB14", "UUID": "EcoFlex-TeleB_PT3_1", "unit": "°C"},
            {"name": "TB15", "UUID": "EcoFlex-TeleB_PT3_2", "unit": "°C"},
            {"name": "TB16", "UUID": "EcoFlex-TeleB_PT3_3", "unit": "°C"},
            {"name": "TB17", "UUID": "EcoFlex-TeleB_PT3_4", "unit": "°C"},
            {"name": "TB18", "UUID": "EcoFlex-TeleB_PT3_5", "unit": "°C"},
            {"name": "TB19", "UUID": "EcoFlex-TeleB_PT3_6", "unit": "°C"},
            {"name": "TB20", "UUID": "EcoFlex-TeleB_PT2_0", "unit": "°C"},
            {"name": "TB21", "UUID": "EcoFlex-TeleB_PT2_1", "unit": "°C"},
            {"name": "TB22", "UUID": "EcoFlex-TeleB_PT2_2", "unit": "°C"},
            {"name": "TB23", "UUID": "EcoFlex-TeleB_PT2_3", "unit": "°C"},
            {"name": "TB24", "UUID": "EcoFlex-TeleB_PT2_4", "unit": "°C"},
            {"name": "TB25", "UUID": "EcoFlex-TeleB_PT2_5", "unit": "°C"},
            {"name": "TB26", "UUID": "EcoFlex-TeleB_PT2_6", "unit": "°C"}
        ]
        self.list_B_DA = [
            {"name": "DB1", "UUID": "EcoFlex-TeleB_PM0_0", "unit": "Pa"},
            {"name": "DB2", "UUID": "EcoFlex-TeleB_PM0_1", "unit": "Pa"},
            {"name": "DB3", "UUID": "EcoFlex-TeleB_PM0_2", "unit": "Pa"},
            {"name": "DB4", "UUID": "EcoFlex-TeleB_PM0_3", "unit": "Pa"},
            {"name": "DB5", "UUID": "EcoFlex-TeleB_PM0_4", "unit": "Pa"},
            {"name": "DB6", "UUID": "EcoFlex-TeleB_PM0_5", "unit": "Pa"},
            {"name": "DB7", "UUID": "EcoFlex-TeleB_PM0_6", "unit": "Pa"},
            {"name": "DB8", "UUID": "EcoFlex-TeleB_PM0_7", "unit": "Pa"}]
        
        self.list_M_TE = [
            {"name": "TM1", "UUID":  "EcoFlex-TeleB_PT1_0", "unit": "°C"}, 
            {"name": "TM2", "UUID":  "EcoFlex-TeleB_PT1_1", "unit": "°C"},
            {"name": "TM3", "UUID":  "EcoFlex-TeleB_PT1_2", "unit": "°C"},
            {"name": "TM4", "UUID":  "EcoFlex-TeleB_PT1_3", "unit": "°C"},
            {"name": "TM5", "UUID":  "EcoFlex-TeleB_PT1_4", "unit": "°C"},
            {"name": "TM6", "UUID":  "EcoFlex-TeleB_PT1_5", "unit": "°C"},
            {"name": "TM7", "UUID":  "EcoFlex-TeleB_PT1_6", "unit": "°C"},
            {"name": "TM8", "UUID":  "EcoFlex-TeleB_PT0_0", "unit": "°C"},
            {"name": "TM9", "UUID":  "EcoFlex-TeleB_PT0_1", "unit": "°C"},
            {"name": "TM10", "UUID": "EcoFlex-TeleB_PT0_2", "unit": "°C"},
            {"name": "TM11", "UUID": "EcoFlex-TeleB_PT0_3", "unit": "°C"},
            {"name": "TM12", "UUID": "EcoFlex-TeleB_PT0_4", "unit": "°C"},
            {"name": "TM13", "UUID": "EcoFlex-TeleB_PT0_5", "unit": "°C"},
            {"name": "TM14", "UUID": "EcoFlex-TeleB_PT0_6", "unit": "°C"},
            {"name": "TM15", "UUID": "EcoFlex-TeleB_PP3_0", "unit": "°C"},
            {"name": "TM16", "UUID": "EcoFlex-TeleB_PP3_1", "unit": "°C"},
            {"name": "TM17", "UUID": "EcoFlex-TeleB_PP3_2", "unit": "°C"},
            {"name": "TM18", "UUID": "EcoFlex-TeleB_PP3_3", "unit": "°C"},
            {"name": "TM19", "UUID": "EcoFlex-TeleB_PP3_4", "unit": "°C"},
            {"name": "TM20", "UUID": "EcoFlex-TeleB_PP3_5", "unit": "°C"},
            {"name": "TM21", "UUID": "EcoFlex-TeleB_PP3_6", "unit": "°C"},
            {"name": "TM22", "UUID": "EcoFlex-TeleB_PP2_0", "unit": "°C"},
            {"name": "TM23", "UUID": "EcoFlex-TeleB_PP2_1", "unit": "°C"},
            {"name": "TM24", "UUID": "EcoFlex-TeleB_PP2_2", "unit": "°C"},
            {"name": "TM25", "UUID": "EcoFlex-TeleB_PP2_3", "unit": "°C"},
            {"name": "TM26", "UUID": "EcoFlex-TeleB_PP2_4", "unit": "°C"},
            {"name": "TM27", "UUID": "EcoFlex-TeleB_PP2_5", "unit": "°C"},
            {"name": "TM28", "UUID": "EcoFlex-TeleB_PP2_6", "unit": "°C"}]
            
        self.list_Mm_TE = [
            {"name": "TM29", "UUID": "EcoFlex-TeleB_PAD7_0", "unit": "°C"}, 
            {"name": "TM30", "UUID": "EcoFlex-TeleB_PAD7_1", "unit": "°C"},
            {"name": "TM31", "UUID": "EcoFlex-TeleB_PAD7_2", "unit": "°C"},
            {"name": "TM32", "UUID": "EcoFlex-TeleB_PAD7_3", "unit": "°C"},
            {"name": "TM33", "UUID": "EcoFlex-TeleB_PAD7_4", "unit": "°C"},
            {"name": "TM34", "UUID": "EcoFlex-TeleB_PAD7_5", "unit": "°C"},
            {"name": "TM35", "UUID": "EcoFlex-TeleB_PAD7_6", "unit": "°C"},
            {"name": "TM36", "UUID": "EcoFlex-TeleB_PAD6_0", "unit": "°C"},
            {"name": "TM37", "UUID": "EcoFlex-TeleB_PAD6_1", "unit": "°C"},
            {"name": "TM38", "UUID": "EcoFlex-TeleB_PAD6_2", "unit": "°C"},
            {"name": "TM39", "UUID": "EcoFlex-TeleB_PAD6_3", "unit": "°C"},
            {"name": "TM40", "UUID": "EcoFlex-TeleB_PAD6_4", "unit": "°C"},
            {"name": "TM41", "UUID": "EcoFlex-TeleB_PAD6_5", "unit": "°C"},
            {"name": "TM42", "UUID": "EcoFlex-TeleB_PAD6_6", "unit": "°C"},
            {"name": "TM43", "UUID": "EcoFlex-TeleB_PAD5_0", "unit": "°C"},
            {"name": "TM44", "UUID": "EcoFlex-TeleB_PAD5_1", "unit": "°C"},
            {"name": "TM45", "UUID": "EcoFlex-TeleB_PAD5_2", "unit": "°C"},
            {"name": "TM46", "UUID": "EcoFlex-TeleB_PAD5_3", "unit": "°C"},
            {"name": "TM47", "UUID": "EcoFlex-TeleB_PAD5_4", "unit": "°C"},
            {"name": "TM48", "UUID": "EcoFlex-TeleB_PAD5_5", "unit": "°C"},
            {"name": "TM49", "UUID": "EcoFlex-TeleB_PAD5_6", "unit": "°C"},
            {"name": "TM50", "UUID": "EcoFlex-TeleB_PAD4_0", "unit": "°C"},
            {"name": "TM51", "UUID": "EcoFlex-TeleB_PAD4_1", "unit": "°C"},
            {"name": "TM52", "UUID": "EcoFlex-TeleB_PAD4_2", "unit": "°C"},
            {"name": "TM53", "UUID": "EcoFlex-TeleB_PAD4_3", "unit": "°C"},
            {"name": "TM54", "UUID": "EcoFlex-TeleB_PAD4_4", "unit": "°C"},
            {"name": "TM55", "UUID": "EcoFlex-TeleB_PAD4_5", "unit": "°C"},
            {"name": "TM56", "UUID": "EcoFlex-TeleB_PAD4_6", "unit": "°C"}]
        
        self.list_IW_TE = [
            {"name": "TIW1", "UUID": "EcoFlex-TeleIW_PP0_0", "unit": "°C"}, 
            {"name": "TIW2", "UUID": "EcoFlex-TeleIW_PP0_1", "unit": "°C"}, 
            {"name": "TIW3", "UUID": "EcoFlex-TeleIW_PP0_2", "unit": "°C"}] 
        
        self.list_IW_LTE = [
            {"name": "TLIW1", "UUID": "EcoFlex-TeleIW_PP1_0", "unit": "°C"},
            {"name": "TLIW2", "UUID": "EcoFlex-TeleIW_PP0_3", "unit": "°C"},
            {"name": "TLIW3", "UUID": "EcoFlex-TeleIW_PP1_1", "unit": "°C"},
            {"name": "TLIW4", "UUID": "EcoFlex-TeleIW_PP1_2", "unit": "°C"},
            {"name": "TLIW5", "UUID": "EcoFlex-TeleIW_PP0_4", "unit": "°C"},
            {"name": "TLIW6", "UUID": "EcoFlex-TeleIW_PP1_3", "unit": "°C"},
            {"name": "TLIW7", "UUID": "EcoFlex-TeleIW_PP1_4", "unit": "°C"},
            {"name": "TLIW8", "UUID": "EcoFlex-TeleIW_PP0_5", "unit": "°C"},
            {"name": "TLIW9", "UUID": "EcoFlex-TeleIW_PP1_5", "unit": "°C"}]
        
        self.list_A_LTE = [
            {"name": "TLA1", "UUID": "EcoFlex-TeleA_PM1_0", "unit": "°C"}, 
            {"name": "TLA2", "UUID": "EcoFlex-TeleA_PM1_1", "unit": "°C"},
            {"name": "TLA3", "UUID": "EcoFlex-TeleA_PM1_2", "unit": "°C"},
            {"name": "TLA4", "UUID": "EcoFlex-TeleA_PM1_3", "unit": "°C"}, 
            {"name": "TLA5", "UUID": "EcoFlex-TeleA_PM1_4", "unit": "°C"},
            {"name": "TLA6", "UUID": "EcoFlex-TeleA_PM1_5", "unit": "°C"}]
        
        self.list_M_LTE = [
            {"name": "TLM1", "UUID": "EcoFlex-TeleB_PM1_0", "unit": "°C"}, 
            {"name": "TLM2", "UUID": "EcoFlex-TeleB_PM1_1", "unit": "°C"},
            {"name": "TLM3", "UUID": "EcoFlex-TeleB_PM1_2", "unit": "°C"},
            {"name": "TLM4", "UUID": "EcoFlex-TeleB_PM1_3", "unit": "°C"}, 
            {"name": "TLM5", "UUID": "EcoFlex-TeleB_PM1_4", "unit": "°C"},
            {"name": "TLM6", "UUID": "EcoFlex-TeleB_PM1_5", "unit": "°C"}]
        
        
        self.tables = [
            [self.scheibeATableTE, self.list_A_TA], 
            [self.scheibeATableDA, self.list_A_DA], 
            [self.scheibeBTableTE, self.list_B_TE], 
            [self.scheibeBTableDA, self.list_B_DA],
            [self.scheibeMTableTE, self.list_M_TE],
            [self.scheibeMMantelTableTE, self.list_Mm_TE],
            [self.innenwelleTableTE, self.list_IW_TE],
            [self.innenwelleTableLTE, self.list_IW_LTE],
            [self.scheibeATableLTE, self.list_A_LTE],
            [self.scheibeMTableLTE, self.list_M_LTE]]
        
        for table in self.tables:
            for i in range (0, table[0].rowCount()):
                
                nameWidget = QTableWidgetItem()
                nameWidget.setText(table[1][i]["name"])
                table[0].setItem(i, 0, nameWidget)
                vauleWidget = QTableWidgetItem()
                vauleWidget.setTextAlignment(Qt.AlignRight)
                # vauleWidget.setTextAlignment(Qt.AlignHCenter)
                table[0].setItem(i, 1, vauleWidget)
                unitWidget = QTableWidgetItem()
                unitWidget.setText(table[1][i]["unit"])
                table[0].setItem(i, 2, unitWidget)
            
        
    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        
        for table in self.tables:
            for i in range (0, len(table[1])):
                uuid = table[1][i]["UUID"]
                valueData = self.findCalibratedDataByUUID(data, dataInfo, uuid)
                if valueData is not None:
                    table[0].item(i, 1).setText("{0:8.2f}".format(valueData))

    def sendData(self):
        pass

    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        return ""

    def load(self, data):
        pass
