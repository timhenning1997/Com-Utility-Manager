import random

from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, \
    QGridLayout, QTableWidget, QTableWidgetItem, QDoubleSpinBox, QAbstractSpinBox, QSpinBox
from PyQt5.QtGui import QPixmap, QFont
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from UsefulFunctions import returnFloat, isFloat
from math import *
from time import *


class WindowSynthetischeDaten(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "SynthetischeDaten")

        self.dataCounter = 1

        self.dataTimer = QTimer(self)
        self.dataTimer.timeout.connect(self.sendCalibratedData)

        self.serialParameters = SerialParameters("COM123", 115200)
        self.serialParameters.Kennung = 7
        self.serialParameters.Kennbin = b'\x07\x01'
        self.serialParameters.readTextIndex = "read_WU_device"

        addColumnButton = QPushButton("+ Column")
        addColumnButton.clicked.connect(self.addColumn)
        deleteColumnButton = QPushButton("- Column")
        deleteColumnButton.clicked.connect(self.deleteLastColumn)

        self.table = QTableWidget(0, 1)
        self.table.setHorizontalHeaderLabels(["UUID"])

        self.errorLineEdit = QLineEdit()
        self.errorLineEdit.setEnabled(False)
        self.errorLineEdit.setStyleSheet("QLineEdit { color: red }")

        addRowButton = QPushButton("+ Row")
        addRowButton.clicked.connect(self.addRow)
        deleteRowButton = QPushButton("- Row")
        deleteRowButton.clicked.connect(self.deleteLastRow)

        #sendRawDataButton = QPushButton("Send Data")
        #sendRawDataButton.clicked.connect(self.sendData)

        sendCalibratedDataButton = QPushButton("Send Calibrated Data")
        sendCalibratedDataButton.clicked.connect(self.sendCalibratedData)

        self.timerSpinBox = QSpinBox()
        self.timerSpinBox.setRange(1, 1000000)
        self.timerSpinBox.setValue(100)
        startTimerButton = QPushButton("Start timer")
        startTimerButton.clicked.connect(self.startTimerClicked)
        stopTimerButton = QPushButton("Stop timer")
        stopTimerButton.clicked.connect(self.stopTimerClicked)

        sendRawAndCalDataButton = QPushButton("Send Calibrated Data")
        sendRawAndCalDataButton.clicked.connect(self.sendRawAndCalData)


        # Layout

        sendButtonLayout = QHBoxLayout()
        #sendButtonLayout.addWidget(sendRawDataButton)
        sendButtonLayout.addWidget(sendCalibratedDataButton)
        sendButtonLayout.addStretch()
        sendButtonLayout.addWidget(self.timerSpinBox)
        sendButtonLayout.addWidget(startTimerButton)
        sendButtonLayout.addWidget(stopTimerButton)

        optionsLayout = QHBoxLayout()
        optionsLayout.addStretch()
        optionsLayout.addWidget(deleteColumnButton)
        optionsLayout.addWidget(addColumnButton)

        options2Layout = QVBoxLayout()
        options2Layout.addWidget(deleteRowButton)
        options2Layout.addWidget(addRowButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(optionsLayout)
        mainLayout.addWidget(self.table)
        mainLayout.addWidget(self.errorLineEdit)
        mainLayout.addLayout(options2Layout)
        mainLayout.addLayout(sendButtonLayout)


        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)


    def addColumn(self):
        self.table.setColumnCount(self.table.columnCount() + 1)
        for i in range(0, self.table.rowCount()):
            valueInputLineEdit = QLineEdit()
            valueInputLineEdit.setAlignment(Qt.AlignHCenter)
            self.table.setCellWidget(i, self.table.columnCount() - 1, valueInputLineEdit)

    def deleteLastColumn(self):
        if self.table.columnCount() > 1:
            self.table.setColumnCount(self.table.columnCount() - 1)

    def addRow(self):
        self.table.setRowCount(self.table.rowCount() + 1)
        uuidInputLineEdit = QLineEdit("M" + str(self.table.rowCount()))
        uuidInputLineEdit.setAlignment(Qt.AlignHCenter)
        self.table.setCellWidget(self.table.rowCount() - 1, 0, uuidInputLineEdit)

        for i in range(1, self.table.columnCount()):
            valueInputSpinBox = QLineEdit()
            valueInputSpinBox.setAlignment(Qt.AlignHCenter)
            self.table.setCellWidget(self.table.rowCount() - 1, i, valueInputSpinBox)

    def deleteLastRow(self):
        if self.table.rowCount() > 1:
            self.table.setRowCount(self.table.rowCount() - 1)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        pass

    def sendData(self):
        value = str(hex(random.randint(0, 65535))[2:])
        self._hubWindow.printReceivedData(self.serialParameters, ['a417', 'b8b6', '5138', value, '0003', '0004', '0005', '0006', '3b10', '4f4b'])

    def sendCalibratedData(self):
        uuidList = []
        dataList = []

        self.errorLineEdit.setText("")

        for y in range(0, self.table.rowCount()):
            for x in range(1, self.table.columnCount()):
                self.table.cellWidget(y, x).setStyleSheet("background-color : transparent")

        for i in range(0, self.table.rowCount()):
            uuidList.append(self.table.cellWidget(i, 0).text())
        if self.dataCounter >= self.table.columnCount():
            self.dataCounter = 1
        if self.table.columnCount() > 1:
            for i in range(0, self.table.rowCount()):
                dataStr = self.table.cellWidget(i, self.dataCounter).text()
                if isFloat(dataStr):
                    dataList.append(returnFloat(dataStr))
                else:
                    try:
                        if isFloat(eval(dataStr)):
                            dataList.append(eval(dataStr))
                    except Exception as e:
                        self.errorLineEdit.setText(str(e))
                        dataList.append(0)
                self.table.cellWidget(i, self.dataCounter).setStyleSheet("background-color : rgba(0, 0, 255, 50)")
            self.dataCounter += 1
        data = {"UUID": uuidList, "DATA": dataList}
        self._hubWindow.printReceivedData(self.serialParameters, data, {"dataType": "CALIBRATED-Values"})

    def sendRawAndCalData(self):
        self.sendData()
        self.sendCalibratedData()

    def startTimerClicked(self):
        self.dataTimer.start(self.timerSpinBox.value())

    def stopTimerClicked(self):
        self.dataTimer.stop()

    def save(self):
        tableData = []
        for y in range(0, self.table.rowCount()):
            rowData = [self.table.cellWidget(y, 0).text()]
            for x in range(1, self.table.columnCount()):
                rowData.append(self.table.cellWidget(y, x).text())
            tableData.append(rowData)
        return {"tableData": tableData,
                "rowCount": self.table.rowCount(),
                "columnCount": self.table.columnCount()}

    def load(self, data):
        for y in range(0, data["rowCount"]):
            self.addRow()
        for x in range(0, data["columnCount"]-1):
            self.addColumn()

        for y in range(0, self.table.rowCount()):
            self.table.cellWidget(y, 0).setText(data["tableData"][y][0])
            for x in range(1, self.table.columnCount()):
                self.table.cellWidget(y, x).setText(data["tableData"][y][x])
