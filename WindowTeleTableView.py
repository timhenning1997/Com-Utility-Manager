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
            {"name": "TA1", "UUID":  "Tele-A_PP0_0", "unit": "°C"}, 
            {"name": "TA2", "UUID":  "Tele-A_PP0_1", "unit": "°C"},
            {"name": "TA3", "UUID":  "Tele-A_PP0_2", "unit": "°C"},
            {"name": "TA4", "UUID":  "Tele-A_PP0_3", "unit": "°C"},
            {"name": "TA5", "UUID":  "Tele-A_PP0_4", "unit": "°C"},
            {"name": "TA6", "UUID":  "Tele-A_PP0_5", "unit": "°C"},
            {"name": "TA7", "UUID":  "Tele-A_PP1_0", "unit": "°C"},
            {"name": "TA8", "UUID":  "Tele-A_PP1_1", "unit": "°C"},
            {"name": "TA9", "UUID":  "Tele-A_PP1_2", "unit": "°C"},
            {"name": "TA10", "UUID": "Tele-A_PP1_3", "unit": "°C"},
            {"name": "TA11", "UUID": "Tele-A_PP1_4", "unit": "°C"},
            {"name": "TA12", "UUID": "Tele-A_PP1_5", "unit": "°C"},
            {"name": "TA13", "UUID": "Tele-A_PP2_0", "unit": "°C"},
            {"name": "TA14", "UUID": "Tele-A_PP2_1", "unit": "°C"},
            {"name": "TA15", "UUID": "Tele-A_PP2_2", "unit": "°C"},
            {"name": "TA16", "UUID": "Tele-A_PP2_3", "unit": "°C"},
            {"name": "TA17", "UUID": "Tele-A_PP2_4", "unit": "°C"},
            {"name": "TA18", "UUID": "Tele-A_PP2_5", "unit": "°C"},
            {"name": "TA19", "UUID": "Tele-A_PP2_6", "unit": "°C"},
            {"name": "TA20", "UUID": "Tele-A_PP3_0", "unit": "°C"},
            {"name": "TA21", "UUID": "Tele-A_PP3_1", "unit": "°C"},
            {"name": "TA22", "UUID": "Tele-A_PP3_2", "unit": "°C"},
            {"name": "TA23", "UUID": "Tele-A_PP3_3", "unit": "°C"},
            {"name": "TA24", "UUID": "Tele-A_PP3_4", "unit": "°C"},
            {"name": "TA25", "UUID": "Tele-A_PP3_5", "unit": "°C"},
            {"name": "TA26", "UUID": "Tele-A_PP3_6", "unit": "°C"}]
        
        self.list_A_DA = [
            {"name": "DA1", "UUID": "Tele-A_PM0_0", "unit": "Pa"},
            {"name": "DA2", "UUID": "Tele-A_PM0_1", "unit": "Pa"},
            {"name": "DA3", "UUID": "Tele-A_PM0_2", "unit": "Pa"},
            {"name": "DA4", "UUID": "Tele-A_PM0_3", "unit": "Pa"},
            {"name": "DA5", "UUID": "Tele-A_PM0_4", "unit": "Pa"},
            {"name": "DA6", "UUID": "Tele-A_PM0_5", "unit": "Pa"},
            {"name": "DA7", "UUID": "Tele-A_PM0_6", "unit": "Pa"},
            {"name": "DA8", "UUID": "Tele-A_PM0_7", "unit": "Pa"}]
        
        self.list_B_TE = [
            {"name": "TB1", "UUID":  "Tele-B_PP0_0", "unit": "°C"}, 
            {"name": "TB2", "UUID":  "Tele-B_PP0_1", "unit": "°C"},
            {"name": "TB3", "UUID":  "Tele-B_PP0_2", "unit": "°C"},
            {"name": "TB4", "UUID":  "Tele-B_PP0_3", "unit": "°C"},
            {"name": "TB5", "UUID":  "Tele-B_PP0_4", "unit": "°C"},
            {"name": "TB6", "UUID":  "Tele-B_PP0_5", "unit": "°C"},
            {"name": "TB7", "UUID":  "Tele-B_PP1_0", "unit": "°C"},
            {"name": "TB8", "UUID":  "Tele-B_PP1_1", "unit": "°C"},
            {"name": "TB9", "UUID":  "Tele-B_PP1_2", "unit": "°C"},
            {"name": "TB10", "UUID": "Tele-B_PP1_3", "unit": "°C"},
            {"name": "TB11", "UUID": "Tele-B_PP1_4", "unit": "°C"},
            {"name": "TB12", "UUID": "Tele-B_PP1_5", "unit": "°C"},
            {"name": "TB13", "UUID": "Tele-B_PT3_0", "unit": "°C"},
            {"name": "TB14", "UUID": "Tele-B_PT3_1", "unit": "°C"},
            {"name": "TB15", "UUID": "Tele-B_PT3_2", "unit": "°C"},
            {"name": "TB16", "UUID": "Tele-B_PT3_3", "unit": "°C"},
            {"name": "TB17", "UUID": "Tele-B_PT3_4", "unit": "°C"},
            {"name": "TB18", "UUID": "Tele-B_PT3_5", "unit": "°C"},
            {"name": "TB19", "UUID": "Tele-B_PT3_6", "unit": "°C"},
            {"name": "TB20", "UUID": "Tele-B_PT2_0", "unit": "°C"},
            {"name": "TB21", "UUID": "Tele-B_PT2_1", "unit": "°C"},
            {"name": "TB22", "UUID": "Tele-B_PT2_2", "unit": "°C"},
            {"name": "TB23", "UUID": "Tele-B_PT2_3", "unit": "°C"},
            {"name": "TB24", "UUID": "Tele-B_PT2_4", "unit": "°C"},
            {"name": "TB25", "UUID": "Tele-B_PT2_5", "unit": "°C"},
            {"name": "TB26", "UUID": "Tele-B_PT2_6", "unit": "°C"}
        ]
        self.list_B_DA = [
            {"name": "DB1", "UUID": "Tele-B_PM0_0", "unit": "Pa"},
            {"name": "DB2", "UUID": "Tele-B_PM0_1", "unit": "Pa"},
            {"name": "DB3", "UUID": "Tele-B_PM0_2", "unit": "Pa"},
            {"name": "DB4", "UUID": "Tele-B_PM0_3", "unit": "Pa"},
            {"name": "DB5", "UUID": "Tele-B_PM0_4", "unit": "Pa"},
            {"name": "DB6", "UUID": "Tele-B_PM0_5", "unit": "Pa"},
            {"name": "DB7", "UUID": "Tele-B_PM0_6", "unit": "Pa"},
            {"name": "DB8", "UUID": "Tele-B_PM0_7", "unit": "Pa"}]
        
        self.list_M_TE = [
            {"name": "TM1", "UUID":  "Tele-B_PT1_0", "unit": "°C"}, 
            {"name": "TM2", "UUID":  "Tele-B_PT1_1", "unit": "°C"},
            {"name": "TM3", "UUID":  "Tele-B_PT1_2", "unit": "°C"},
            {"name": "TM4", "UUID":  "Tele-B_PT1_3", "unit": "°C"},
            {"name": "TM5", "UUID":  "Tele-B_PT1_4", "unit": "°C"},
            {"name": "TM6", "UUID":  "Tele-B_PT1_5", "unit": "°C"},
            {"name": "TM7", "UUID":  "Tele-B_PT1_6", "unit": "°C"},
            {"name": "TM8", "UUID":  "Tele-B_PT0_0", "unit": "°C"},
            {"name": "TM9", "UUID":  "Tele-B_PT0_1", "unit": "°C"},
            {"name": "TM10", "UUID": "Tele-B_PT0_2", "unit": "°C"},
            {"name": "TM11", "UUID": "Tele-B_PT0_3", "unit": "°C"},
            {"name": "TM12", "UUID": "Tele-B_PT0_4", "unit": "°C"},
            {"name": "TM13", "UUID": "Tele-B_PT0_5", "unit": "°C"},
            {"name": "TM14", "UUID": "Tele-B_PT0_6", "unit": "°C"},
            {"name": "TM15", "UUID": "Tele-B_PP3_0", "unit": "°C"},
            {"name": "TM16", "UUID": "Tele-B_PP3_1", "unit": "°C"},
            {"name": "TM17", "UUID": "Tele-B_PP3_2", "unit": "°C"},
            {"name": "TM18", "UUID": "Tele-B_PP3_3", "unit": "°C"},
            {"name": "TM19", "UUID": "Tele-B_PP3_4", "unit": "°C"},
            {"name": "TM20", "UUID": "Tele-B_PP3_5", "unit": "°C"},
            {"name": "TM21", "UUID": "Tele-B_PP3_6", "unit": "°C"},
            {"name": "TM22", "UUID": "Tele-B_PP2_0", "unit": "°C"},
            {"name": "TM23", "UUID": "Tele-B_PP2_1", "unit": "°C"},
            {"name": "TM24", "UUID": "Tele-B_PP2_2", "unit": "°C"},
            {"name": "TM25", "UUID": "Tele-B_PP2_3", "unit": "°C"},
            {"name": "TM26", "UUID": "Tele-B_PP2_4", "unit": "°C"},
            {"name": "TM27", "UUID": "Tele-B_PP2_5", "unit": "°C"},
            {"name": "TM28", "UUID": "Tele-B_PP2_6", "unit": "°C"}]
            
        self.list_Mm_TE = [
            {"name": "TM29", "UUID": "Tele-B_PAD7_0", "unit": "°C"}, 
            {"name": "TM30", "UUID": "Tele-B_PAD7_1", "unit": "°C"},
            {"name": "TM31", "UUID": "Tele-B_PAD7_2", "unit": "°C"},
            {"name": "TM32", "UUID": "Tele-B_PAD7_3", "unit": "°C"},
            {"name": "TM33", "UUID": "Tele-B_PAD7_4", "unit": "°C"},
            {"name": "TM34", "UUID": "Tele-B_PAD7_5", "unit": "°C"},
            {"name": "TM35", "UUID": "Tele-B_PAD7_6", "unit": "°C"},
            {"name": "TM36", "UUID": "Tele-B_PAD6_0", "unit": "°C"},
            {"name": "TM37", "UUID": "Tele-B_PAD6_1", "unit": "°C"},
            {"name": "TM38", "UUID": "Tele-B_PAD6_2", "unit": "°C"},
            {"name": "TM39", "UUID": "Tele-B_PAD6_3", "unit": "°C"},
            {"name": "TM40", "UUID": "Tele-B_PAD6_4", "unit": "°C"},
            {"name": "TM41", "UUID": "Tele-B_PAD6_5", "unit": "°C"},
            {"name": "TM42", "UUID": "Tele-B_PAD6_6", "unit": "°C"},
            {"name": "TM43", "UUID": "Tele-B_PAD5_0", "unit": "°C"},
            {"name": "TM44", "UUID": "Tele-B_PAD5_1", "unit": "°C"},
            {"name": "TM45", "UUID": "Tele-B_PAD5_2", "unit": "°C"},
            {"name": "TM46", "UUID": "Tele-B_PAD5_3", "unit": "°C"},
            {"name": "TM47", "UUID": "Tele-B_PAD5_4", "unit": "°C"},
            {"name": "TM48", "UUID": "Tele-B_PAD5_5", "unit": "°C"},
            {"name": "TM49", "UUID": "Tele-B_PAD5_6", "unit": "°C"},
            {"name": "TM50", "UUID": "Tele-B_PAD4_0", "unit": "°C"},
            {"name": "TM51", "UUID": "Tele-B_PAD4_1", "unit": "°C"},
            {"name": "TM52", "UUID": "Tele-B_PAD4_2", "unit": "°C"},
            {"name": "TM53", "UUID": "Tele-B_PAD4_3", "unit": "°C"},
            {"name": "TM54", "UUID": "Tele-B_PAD4_4", "unit": "°C"},
            {"name": "TM55", "UUID": "Tele-B_PAD4_5", "unit": "°C"},
            {"name": "TM56", "UUID": "Tele-B_PAD4_6", "unit": "°C"}]
        
        self.list_IW_TE = [
            {"name": "TIW1", "UUID": "Tele-IW_PP0_0", "unit": "°C"}, 
            {"name": "TIW2", "UUID": "Tele-IW_PP0_1", "unit": "°C"}, 
            {"name": "TIW3", "UUID": "Tele-IW_PP0_2", "unit": "°C"}] 
        
        self.list_IW_LTE = [
            {"name": "TLIW1", "UUID": "Tele-IW_PP1_0", "unit": "°C"},
            {"name": "TLIW2", "UUID": "Tele-IW_PP0_3", "unit": "°C"},
            {"name": "TLIW3", "UUID": "Tele-IW_PP1_1", "unit": "°C"},
            {"name": "TLIW4", "UUID": "Tele-IW_PP1_2", "unit": "°C"},
            {"name": "TLIW5", "UUID": "Tele-IW_PP0_4", "unit": "°C"},
            {"name": "TLIW6", "UUID": "Tele-IW_PP1_3", "unit": "°C"},
            {"name": "TLIW7", "UUID": "Tele-IW_PP1_4", "unit": "°C"},
            {"name": "TLIW8", "UUID": "Tele-IW_PP0_5", "unit": "°C"},
            {"name": "TLIW9", "UUID": "Tele-IW_PP1_5", "unit": "°C"}]
        
        self.list_A_LTE = [
            {"name": "TLA1", "UUID": "Tele-A_PM1_0", "unit": "°C"}, 
            {"name": "TLA2", "UUID": "Tele-A_PM1_1", "unit": "°C"},
            {"name": "TLA3", "UUID": "Tele-A_PM1_2", "unit": "°C"},
            {"name": "TLA4", "UUID": "Tele-A_PM1_3", "unit": "°C"}, 
            {"name": "TLA5", "UUID": "Tele-A_PM1_4", "unit": "°C"},
            {"name": "TLA6", "UUID": "Tele-A_PM1_5", "unit": "°C"}]
        
        self.list_M_LTE = [
            {"name": "TLM1", "UUID": "Tele-B_PM1_0", "unit": "°C"}, 
            {"name": "TLM2", "UUID": "Tele-B_PM1_1", "unit": "°C"},
            {"name": "TLM3", "UUID": "Tele-B_PM1_2", "unit": "°C"},
            {"name": "TLM4", "UUID": "Tele-B_PM1_3", "unit": "°C"}, 
            {"name": "TLM5", "UUID": "Tele-B_PM1_4", "unit": "°C"},
            {"name": "TLM6", "UUID": "Tele-B_PM1_5", "unit": "°C"}]
        
        
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
