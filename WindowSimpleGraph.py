import time

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QFont, QPen, QColor
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, \
    QTableWidget, QHeaderView, QTableWidgetItem, QSpinBox, QMessageBox, QSplitter, QAction, QDoubleSpinBox, QCheckBox
from PyQt5.QtCore import Qt
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from pyqtgraph import PlotWidget, plot, mkPen
from numpy import polyfit


class GraphLine:
    def __init__(self, UUID: str, startTime: float = 0):
        self.UUID = UUID
        self.startTime = startTime
        self.lastDataTime = 0
        self.x = []
        self.y = []
        self.dataLine = None

        self.maxLength = 200
        self.maxSamplingRate = 5

    def appendDataPoint(self, y: float, x: float = None):
        if self.dataLine is None:
            return
        if time.time() < self.lastDataTime + 1/self.maxSamplingRate:
            return
        self.lastDataTime = time.time()
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


class WindowSimpleGraph(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "SimpleGraph")

        self.graphLines = {}
        self.dataCounter = 0
        self.graphStartTime = time.time()

        self._maxDataPoints = 200
        self._maxSamplingRate = 5

        self.colorCounter = 0
        #self.colorTable = ["#c095e3", "#fff384", "#53af8b", "#e3adb5", "#95b8e3", "#a99887", "#f69284", "#95dfe3", "#f0b892"]
        self.colorTable = ["#E61D66", "#1E88E5", "#FFC107", "#12F5CF", "#14C944", "#EF7290", "#FE1A00", "#1FB2E0",
                           "#C47DE4", "#FF2F97", "#BAE45D", "#FB88A5", "#5391CA", "#C8DEAB", "#DFAD5C", "#E3531E",
                           "#3AD00B", "#E7C6EE", "#2465F8"]
        self.graphWidget = PlotWidget()
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground(None)
        self.graphWidget.addLegend()

        maxDataPointsLabel = QLabel("Max Data Points:")

        self.maxValueSpinBox = QSpinBox()
        self.maxValueSpinBox.setRange(1, 10000)
        self.maxValueSpinBox.setValue(200)
        self.maxValueSpinBox.editingFinished.connect(self.maxValueChanged)

        maxSamplingRateLabel = QLabel("Max Sampling Rate [Hz]:")

        self.maxSamplingSpinBox = QDoubleSpinBox()
        self.maxSamplingSpinBox.setRange(0.0001, 10000)
        self.maxSamplingSpinBox.setDecimals(4)
        self.maxSamplingSpinBox.setValue(5)
        self.maxSamplingSpinBox.editingFinished.connect(self.maxSamplingChanged)

        maxDataPointsLayout = QHBoxLayout()
        maxDataPointsLayout.addWidget(maxDataPointsLabel)
        maxDataPointsLayout.addWidget(self.maxValueSpinBox)

        maxSamplingRateLayout = QHBoxLayout()
        maxSamplingRateLayout.addWidget(maxSamplingRateLabel)
        maxSamplingRateLayout.addWidget(self.maxSamplingSpinBox)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["", "UUID", "Name", "Unit", "Last Value", "Del"])
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 10)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 30)
        self.table.setColumnWidth(5, 20)

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
        verticalLayout.addLayout(maxSamplingRateLayout)
        verticalLayout.addWidget(self.table)
        verticalLayout.addLayout(addNameLayout)
        tableWidget = QWidget()
        tableWidget.setLayout(verticalLayout)

        graphSplitter = QSplitter(Qt.Horizontal)
        graphSplitter.addWidget(self.graphWidget)
        graphSplitter.addWidget(tableWidget)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(graphSplitter)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def initUI(self):
        self.setWindowTitle(self._windowType)

        tableMenu = QMenu("&Table", self)
        act = QAction("Show/Hide Columns", self)
        act.setEnabled(False)
        font1 = QFont()
        font1.setUnderline(True)
        act.setFont(font1)
        tableMenu.addAction(act)
        self.actShowColor = QAction('&Color', self, triggered=lambda obj: self.tableShowColumn(0, obj))
        self.actShowColor.setCheckable(True)
        self.actShowColor.setChecked(True)
        self.actShowUUID = QAction('&UUID', self, triggered=lambda obj: self.tableShowColumn(1, obj))
        self.actShowUUID.setCheckable(True)
        self.actShowUUID.setChecked(True)
        self.actShowName = QAction('&Name', self, triggered=lambda obj: self.tableShowColumn(2, obj))
        self.actShowName.setCheckable(True)
        self.actShowName.setChecked(True)
        self.actShowUnit = QAction('&Unit', self, triggered=lambda obj: self.tableShowColumn(3, obj))
        self.actShowUnit.setCheckable(True)
        self.actShowUnit.setChecked(True)
        self.actShowLastValue = QAction('&Last value', self, triggered=lambda obj: self.tableShowColumn(4, obj))
        self.actShowLastValue.setCheckable(True)
        self.actShowLastValue.setChecked(True)
        self.actShowDelete = QAction('&Delete', self, triggered=lambda obj: self.tableShowColumn(5, obj))
        self.actShowDelete.setCheckable(True)
        self.actShowDelete.setChecked(True)
        tableMenu.addAction(self.actShowColor)
        tableMenu.addAction(self.actShowUUID)
        tableMenu.addAction(self.actShowName)
        tableMenu.addAction(self.actShowUnit)
        tableMenu.addAction(self.actShowLastValue)
        tableMenu.addAction(self.actShowDelete)
        self.menuBar().addMenu(tableMenu)


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
                    UUID = self.addNameLineEdit.text()
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

        #widget = QWidget()
        #layout = QVBoxLayout()
        #legendBarLabel = QLabel()
        #legendBarLabel.setStyleSheet("QLabel {background-color: " + self.colorTable[self.colorCounter] + "}")
        #legendBarLabel.setFixedSize(20, 4)
        #layout.addStretch()
        #layout.addWidget(legendBarLabel)
        #layout.addStretch()
        #widget.setLayout(layout)
        #widget.setProperty("UUID", measuringPointUUID)

        widget = QCheckBox()
        widget.clicked.connect(lambda: self.highlightedCheckboxPressed(widget, measuringPointUUID))
        widget.setStyleSheet('QCheckBox::indicator{border:1px solid ' +
                             self.colorTable[self.colorCounter] +
                             '}QCheckBox::indicator::checked{background-color : ' +
                             self.colorTable[self.colorCounter] + '}')
        # widget.setStyleSheet('border: 1px solid; border-color: ' + self.colorTable[self.colorCounter])
        widget.setProperty("COLOR", self.colorTable[self.colorCounter])
        tempWidget = QWidget()
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()
        layout.setContentsMargins(1, 1, 1, 1)
        tempWidget.setLayout(layout)
        tempWidget.setProperty("UUID", measuringPointUUID)
        self.table.setCellWidget(self.table.rowCount() - 1, 0, tempWidget)

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

        self.graphLines[measuringPointUUID] = GraphLine(measuringPointUUID, self.graphStartTime)
        pen = mkPen(color=self.colorTable[self.colorCounter])
        if self.colorCounter >= len(self.colorTable) - 1:
            self.colorCounter = 0
        else:
            self.colorCounter += 1
        self.graphLines[measuringPointUUID].dataLine = self.graphWidget.plot([], [], pen=pen, name=UUID)
        self.graphLines[measuringPointUUID].maxLength = self.maxValueSpinBox.value()

    def tableFindComRow(self, UUID: str):
        for countY in range(0, self.table.rowCount()):
            if self.table.item(countY, 1).text() == UUID:
                return countY
        return None

    def tableShowColumn(self, column: int, checked: bool):
        if checked:
            self.table.showColumn(column)
        else:
            self.table.hideColumn(column)

    def deleteButtonPressed(self, UUID: str):
        self.table.removeRow(self.tableFindComRow(UUID))
        self.graphLines[UUID].dataLine.clear()
        del self.graphLines[UUID]

    def highlightedCheckboxPressed(self, checkbox: QCheckBox, UUID: str):
        if checkbox.isChecked():
            new_pen = mkPen(checkbox.property("COLOR"), width=4)
        else:
            new_pen = mkPen(checkbox.property("COLOR"), width=1)
        self.graphLines[UUID].dataLine.setPen(new_pen)

    def maxValueChanged(self):
        for key in self.graphLines.keys():
            self.graphLines[key].maxLength = self.maxValueSpinBox.value()
        self._maxDataPoints = self.maxValueSpinBox.value()

    def maxSamplingChanged(self):
        for key in self.graphLines.keys():
            self.graphLines[key].maxSamplingRate = self.maxSamplingSpinBox.value()
        self._maxSamplingRate = self.maxSamplingSpinBox.value()

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        self.dataCounter += 1
        for key in self.graphLines.keys():
            value = self.findCalibratedDataByUUID(data, dataInfo, key)
            if value is not None:
                self.graphLines[key].appendDataPoint(value) #, self.dataCounter)
                self.table.item(self.tableFindComRow(key), 4).setText("{:.2f}".format(value))

    def sendData(self):
        pass

    def save(self):
        tempSave = []
        for countY in range(0, self.table.rowCount()):
            saveName = self.table.cellWidget(countY, 0).property("UUID")
            tempSave.append(saveName)

        tableColumnShown = []
        for countX in range(0, self.table.columnCount()):
            tableColumnShown.append(self.table.isColumnHidden(countX))

        return {"tempSave": tempSave,
                "_tableColumnsHidden": tableColumnShown,
                "maxDataPoints": self._maxDataPoints,
                "maxSamplingRate": self._maxSamplingRate}

    def load(self, data):
        for saveName in data["tempSave"]:
            self.addDataLine("", saveName)

        self.actShowColor.setChecked(not data['_tableColumnsHidden'][0])
        self.actShowUUID.setChecked(not data['_tableColumnsHidden'][1])
        self.actShowName.setChecked(not data['_tableColumnsHidden'][2])
        self.actShowUnit.setChecked(not data['_tableColumnsHidden'][3])
        self.actShowLastValue.setChecked(not data['_tableColumnsHidden'][4])
        self.actShowDelete.setChecked(not data['_tableColumnsHidden'][5])

        for countX in range(0, self.table.columnCount()):
            self.table.hideColumn(countX) if data['_tableColumnsHidden'][countX] else self.table.showColumn(countX)

        self.maxValueSpinBox.setValue(data['maxDataPoints'])
        self.maxSamplingSpinBox.setValue(data['maxSamplingRate'])
