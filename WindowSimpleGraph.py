from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, \
    QTableWidget, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from pyqtgraph import PlotWidget, plot, mkPen
from random import randint


class GraphLine:
    def __init__(self, UUID: str):
        self.UUID = UUID
        self.x = []
        self.y = []
        self.dataLine = None

        self.maxLength = 200

    def appendDataPoint(self, x: float, y: float):
        if self.dataLine is None:
            print("NONE_____________________________", self.UUID, x, y)
            return
        if len(self.x) > self.maxLength > 0:
            self.x = self.x[-self.maxLength:]
            self.y = self.y[-self.maxLength:]
            self.x.append(x)
            self.y.append(y)
        else:
            self.x.append(x)
            self.y.append(y)
        self.dataLine.setData(self.x, self.y)


class WindowSimpleGraph(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "SimpleGraph")

        self.graphLines = {}
        self.dataCounter = 0

        self.colorCounter = 0
        self.colorTable = ["#c095e3", "#fff384", "#53af8b", "#e3adb5", "#95b8e3", "#a99887", "#f69284", "#95dfe3", "3f2b44", "#f0b892"]

        self.graphWidget = PlotWidget()
        self.graphWidget.setBackground(None)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["", "UUID", "Name", "Unit", "Last Value", "Del"])
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 20)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 30)
        self.table.setColumnWidth(5, 20)

        addNameLabel = QLabel("UUID:")
        self.addNameLineEdit = QLineEdit("GeraetXY_Messstelle_Z0")
        self.addNameButton = QPushButton("+")
        self.addNameButton.clicked.connect(self.addDataLine)

        addNameLayout = QHBoxLayout()
        addNameLayout.addWidget(addNameLabel)
        addNameLayout.addWidget(self.addNameLineEdit)
        addNameLayout.addWidget(self.addNameButton)

        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.table)
        verticalLayout.addLayout(addNameLayout)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.graphWidget)
        mainLayout.addLayout(verticalLayout)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)



    def addDataLine(self, UUID: str = ""):
        if UUID != False:
            measuringPointInfo = self.findMeasuringPointInfoByUUID(UUID)
        else:
            measuringPointInfo = self.findMeasuringPointInfoByUUID(self.addNameLineEdit.text())

        if measuringPointInfo is not None and "UUID" in measuringPointInfo.keys():

            measuringPointUUID = ""
            measuringPointName = ""
            measuringPointUnit = ""

            if "UUID" in measuringPointInfo.keys():
                measuringPointUUID = measuringPointInfo["UUID"]
            if "Messstelle" in measuringPointInfo.keys():
                measuringPointName = measuringPointInfo["Messstelle"]
            if "Einheit" in measuringPointInfo.keys():
                measuringPointUnit = measuringPointInfo["Einheit"]

            if measuringPointUUID in self.graphLines.keys():
                return

            self.table.insertRow(self.table.rowCount())

            widget = QWidget()
            layout = QVBoxLayout()
            legendBarLabel = QLabel()
            legendBarLabel.setStyleSheet("QLabel {background-color: " + self.colorTable[self.colorCounter] + "}")
            legendBarLabel.setFixedSize(20, 4)
            layout.addStretch()
            layout.addWidget(legendBarLabel)
            layout.addStretch()
            widget.setLayout(layout)
            widget.setProperty("UUID", measuringPointUUID)
            self.table.setCellWidget(self.table.rowCount() - 1, 0, widget)

            self.table.setItem(self.table.rowCount() - 1, 1, QTableWidgetItem(measuringPointUUID))
            self.table.item(self.table.rowCount() - 1, 1).setTextAlignment(Qt.AlignCenter)
            self.table.item(self.table.rowCount() - 1, 1).setFlags(Qt.ItemIsEnabled)

            self.table.setItem(self.table.rowCount() - 1, 2, QTableWidgetItem(measuringPointName))
            self.table.item(self.table.rowCount() - 1, 2).setTextAlignment(Qt.AlignCenter)
            self.table.item(self.table.rowCount() - 1, 2).setFlags(Qt.ItemIsEnabled)

            self.table.setItem(self.table.rowCount() - 1, 3, QTableWidgetItem(measuringPointUnit))
            self.table.item(self.table.rowCount() - 1, 3).setTextAlignment(Qt.AlignCenter)
            self.table.item(self.table.rowCount() - 1, 3).setFlags(Qt.ItemIsEnabled)

            self.table.setItem(self.table.rowCount() - 1, 4, QTableWidgetItem(""))
            self.table.item(self.table.rowCount() - 1, 4).setTextAlignment(Qt.AlignCenter)
            self.table.item(self.table.rowCount() - 1, 4).setFlags(Qt.ItemIsEnabled)

            deleteButton = QPushButton("x")
            deleteButton.setStyleSheet("background-color : red")
            deleteButton.clicked.connect(lambda: self.deleteButtonPressed(measuringPointUUID))
            self.table.setCellWidget(self.table.rowCount() - 1, 5, deleteButton)

            self.graphLines[measuringPointUUID] = GraphLine(measuringPointUUID)
            pen = mkPen(color=self.colorTable[self.colorCounter])
            if self.colorCounter >= len(self.colorTable) - 1:
                self.colorCounter = 0
            else:
                self.colorCounter += 1
            self.graphLines[measuringPointUUID].dataLine = self.graphWidget.plot([], [], pen=pen)


    def tableFindComRow(self, UUID: str):
        for countY in range(0, self.table.rowCount()):
            if self.table.item(countY, 1).text() == UUID:
                return countY
        return None

    def deleteButtonPressed(self, UUID: str):
        self.table.removeRow(self.tableFindComRow(UUID))
        self.graphLines[UUID].dataLine.clear()
        del self.graphLines[UUID]


    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        self.dataCounter += 1
        for key in self.graphLines.keys():
            value = self.findCalibratedDataByUUID(data, dataInfo, key)
            if value is not None:
                self.graphLines[key].appendDataPoint(self.dataCounter, value)
                self.table.item(self.tableFindComRow(key), 4).setText("{:.4f}".format(value))

    def sendData(self):
        pass

    def save(self):
        tempSave = []
        for countY in range(0, self.table.rowCount()):
            saveName = self.table.cellWidget(countY, 0).property("UUID")
            tempSave.append(saveName)

        return tempSave

    def load(self, data):
        for saveName in data:
            self.addDataLine(saveName)
