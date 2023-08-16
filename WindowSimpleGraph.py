import time

from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, \
    QTableWidget, QHeaderView, QTableWidgetItem, QSpinBox, QMessageBox
from PyQt5.QtCore import Qt
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from pyqtgraph import PlotWidget, plot, mkPen
from numpy import polyfit


class GraphLine:
    def __init__(self, UUID: str, startTime: float = 0):
        self.UUID = UUID
        self.startTime = startTime
        self.x = []
        self.y = []
        self.dataLine = None

        self.maxLength = 200

    def appendDataPoint(self, y: float, x: float = None):
        if self.dataLine is None:
            return
        if x is None:
            x = time.time() - self.startTime
        if len(self.x) > self.maxLength > 0:
            self.x = self.x[-self.maxLength:]
            self.y = self.y[-self.maxLength:]
            self.x.append(x)
            self.y.append(y)
        else:
            self.x.append(x)
            self.y.append(y)
        self.dataLine.setData(self.x, self.y)

    def calculateFit(self):
        p = polyfit(self.x, self.y, 1)
        #return str(polyfit(self.x, self.y, 1))
        return str("{:.3f}".format(p[0]))


class WindowSimpleGraph(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "SimpleGraph")

        self.graphLines = {}
        self.dataCounter = 0
        self.graphStartTime = time.time()

        self.colorCounter = 0
        self.colorTable = ["#c095e3", "#fff384", "#53af8b", "#e3adb5", "#95b8e3", "#a99887", "#f69284", "#95dfe3", "#3f2b44", "#f0b892"]

        self.graphWidget = PlotWidget()
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground(None)

        maxDataPointsLabel = QLabel("Max Data Points:")

        self.maxValueSpinBox = QSpinBox()
        self.maxValueSpinBox.setRange(1, 10000)
        self.maxValueSpinBox.setValue(200)
        self.maxValueSpinBox.editingFinished.connect(self.maxValueChanged)

        maxDataPointsLayout = QHBoxLayout()
        maxDataPointsLayout.addWidget(maxDataPointsLabel)
        maxDataPointsLayout.addWidget(self.maxValueSpinBox)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["", "UUID", "Name", "Unit", "Last Value", "Fit slope", "Del"])
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 20)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 30)
        self.table.setColumnWidth(6, 20)

        addNameLabel = QLabel("UUID:")
        self.addNameLineEdit = QLineEdit("GeraetXY_Messstelle_Z0")
        self.addNameLineEdit.returnPressed.connect(self.addDataLine)
        self.addNameButton = QPushButton("+")
        self.addNameButton.clicked.connect(self.addDataLine)

        addNameLayout = QHBoxLayout()
        addNameLayout.addWidget(addNameLabel)
        addNameLayout.addWidget(self.addNameLineEdit)
        addNameLayout.addWidget(self.addNameButton)

        verticalLayout = QVBoxLayout()
        verticalLayout.addLayout(maxDataPointsLayout)
        verticalLayout.addWidget(self.table)
        verticalLayout.addLayout(addNameLayout)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.graphWidget)
        mainLayout.addLayout(verticalLayout)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)


    def returnMsgBoxAnswerYesNo(self, title: str = "Message", text: str = ""):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        return dlg.exec()

    def addDataLine(self, text: str = "", UUID: str = ""):
        measuringPointInfo = {}
        if UUID != "":
            measuringPointInfo = self.findMeasuringPointInfoByUUID(UUID)
        else:
            measuringPointInfo = self.findMeasuringPointInfoByUUID(self.addNameLineEdit.text())

        if measuringPointInfo is None or "UUID" not in measuringPointInfo.keys():
            if UUID == "":
                if self.returnMsgBoxAnswerYesNo("UUID not found", "UUID not found.\nDo you still want to add them?") == QMessageBox.Yes:
                    measuringPointInfo = {"UUID": self.addNameLineEdit.text()}
                else:
                    return
            else:
                measuringPointInfo = {"UUID": UUID}

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

        self.table.setItem(self.table.rowCount() - 1, 5, QTableWidgetItem(""))
        self.table.item(self.table.rowCount() - 1, 5).setTextAlignment(Qt.AlignCenter)
        self.table.item(self.table.rowCount() - 1, 5).setFlags(Qt.ItemIsEnabled)

        deleteButton = QPushButton("x")
        deleteButton.setStyleSheet("background-color : red")
        deleteButton.clicked.connect(lambda: self.deleteButtonPressed(measuringPointUUID))
        self.table.setCellWidget(self.table.rowCount() - 1, 6, deleteButton)

        self.graphLines[measuringPointUUID] = GraphLine(measuringPointUUID, self.graphStartTime)
        pen = mkPen(color=self.colorTable[self.colorCounter])
        if self.colorCounter >= len(self.colorTable) - 1:
            self.colorCounter = 0
        else:
            self.colorCounter += 1
        self.graphLines[measuringPointUUID].dataLine = self.graphWidget.plot([], [], pen=pen)
        self.graphLines[measuringPointUUID].maxLength = self.maxValueSpinBox.value()


    def tableFindComRow(self, UUID: str):
        for countY in range(0, self.table.rowCount()):
            if self.table.item(countY, 1).text() == UUID:
                return countY
        return None

    def deleteButtonPressed(self, UUID: str):
        self.table.removeRow(self.tableFindComRow(UUID))
        self.graphLines[UUID].dataLine.clear()
        del self.graphLines[UUID]

    def maxValueChanged(self):
        for key in self.graphLines.keys():
            self.graphLines[key].maxLength = self.maxValueSpinBox.value()

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        self.dataCounter += 1
        for key in self.graphLines.keys():
            value = self.findCalibratedDataByUUID(data, dataInfo, key)
            if value is not None:
                self.graphLines[key].appendDataPoint(value) #, self.dataCounter)
                self.table.item(self.tableFindComRow(key), 4).setText("{:.4f}".format(value))

                if self.dataCounter % 10 == 0:
                    self.table.item(self.tableFindComRow(key), 5).setText(self.graphLines[key].calculateFit())

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
            self.addDataLine("", saveName)
