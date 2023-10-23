import os
import random
import re
import time
from datetime import datetime
from csv import writer
from pathlib import Path

from PyQt5.QtCore import QPoint, Qt, QTimer, QSize
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, \
    QGridLayout, QTabWidget, QTextEdit, QComboBox, QSplitter, QTableWidget, QSpinBox, QScrollArea, QFileDialog, \
    QCheckBox, QDoubleSpinBox
from PyQt5.QtGui import QPixmap, QFont, QTextCursor, QColor, QIcon
from pyqtgraph import PlotWidget, mkPen

from AbstractWindow import AbstractWindow
from UsefulFunctions import resource_path
from SerialParameters import SerialParameters


class GraphLine:
    def __init__(self,startTime: float = 0):
        self.startTime = startTime
        self.x = []
        self.y = []
        self.dataLine = None

        self.maxLength = 4000

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


class WindowTempCalFritoese(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "TempCalFritteuse")

        self.lastState = "idle"
        self.currentState = "idle"
        self.isActiveCommunication = False
        self.commMessageBacklog = []
        self.currentCommMassage = []
        self.maxCommBacklogSize = 3

        self.tempInBoundsStartTimer = 0

        self.portFilter = []#["COM4"]
        self.incomingDataBuffer = {}
        self.saveDataBuffer = []
        self.gatheredDataCounter = 0
        self._separateFileStr = ""

        self.filePath = str(Path(os.getcwd()))
        self.fileName = "calibration"
        self.currentWorkingRow = 0
        self.setPointTemp = 40
        self.setPointHex = 0
        self.setPointDiffReached = 500
        self.setPointDiffHold = 500
        self.holdTime = 0
        self.requiredDataNumber = 5

        self.graphLines = {}
        self.dataCounter = 0
        self.graphStartTime = time.time()

        self.waitforAnswerTimer = QTimer(self)
        self.waitforAnswerTimer.timeout.connect(self.noAnswerReceived)
        self.waitforAnswerTimer.setInterval(1000)
        self.waitforAnswerTimer.setSingleShot(True)

        self.stateMachineDelayTimer = QTimer(self)
        self.stateMachineDelayTimer.timeout.connect(self.runStateMachine)
        self.stateMachineDelayTimer.setSingleShot(True)

        self.askForCurrentTempTimer = QTimer(self)
        self.askForCurrentTempTimer.timeout.connect(self.askForTemp)
        self.askForCurrentTempTimer.start(2500)

        self.addressDict = {"00": ["vSP", "Setpoint, temperature controller", "0.01°C"],
                            "01": ["vTI", "Internal temperature", "0.01°C"],
                            "02": ["vTR", "Return temperature", "0.01°C"],
                            "03": ["vpP", "Pump pressure (absolute)", "1mbar"],
                            "04": ["vPow", "Current power", "1W"],
                            "05": ["vError", "Error report", ""],
                            "06": ["vWarn", "Warning message", ""],
                            "07": ["vTE", "Process temperature (Lemosa)", "0.01°C"],
                            "08": ["vIntMove", "Actual value setting, Internal temperature", "0.01°C"],
                            "09": ["vExtMove", "Setting, Process temperature", "0.01°C"],
                            "0A": ["vStatus1", "Status of the thermostat", ""],
                            "0B": ["vBDPos", "Control blow-down valve", ""],
                            "14": ["vTmpActive", "Temperature control [0-off; 1-on]", ""],
                            "71": ["vSPT", "Setpoint, temperature controller", "0.01°C"],
                            }

        # _____________________Tab Settings____________________
        fritteusenComPortLabel = QLabel("Fritteusen COM")
        fritteusenComPortLabel.setFixedWidth(100)
        self.fritteusenComPortLineEdit = QLineEdit("")
        self.fritteusenComPortLineEdit.setPlaceholderText("COMXY")
        self.fritteusenComPortLineEdit.setFixedWidth(60)
        fritteusenComPortLayout = QHBoxLayout()
        fritteusenComPortLayout.addWidget(fritteusenComPortLabel)
        fritteusenComPortLayout.addWidget(self.fritteusenComPortLineEdit)
        fritteusenComPortLayout.addStretch()

        filePathLabel = QLabel("File path")
        filePathLabel.setFixedWidth(100)
        self.openFilePathDialogButton = QPushButton()
        self.openFilePathDialogButton.setFixedWidth(40)
        self.openFilePathDialogButton.setIcon(QIcon(resource_path("res/Icon/folder.ico")))
        self.openFilePathDialogButton.setIconSize(QSize(25, 25))
        self.openFilePathDialogButton.clicked.connect(self.openFilePathButtonPressed)
        self.showFilePathLabel = QLabel(str(Path(os.getcwd())))
        filePathLayout = QHBoxLayout()
        filePathLayout.addWidget(filePathLabel)
        filePathLayout.addWidget(self.openFilePathDialogButton)
        filePathLayout.addWidget(self.showFilePathLabel)

        fileNameLabel = QLabel("File name")
        fileNameLabel.setFixedWidth(100)
        self.fileNameLineEdit = QLineEdit("DATE_TIME_calibration")
        self.fileNameLineEdit.setToolTip("DATE: replaced to jjjj-mm-dd | TIME: replaced to hh-mm-ss")
        fileExtensionLabel = QLabel(".txt")
        fileExtensionLabel.setFixedWidth(60)
        fileNameLayout = QHBoxLayout()
        fileNameLayout.addWidget(fileNameLabel)
        fileNameLayout.addWidget(self.fileNameLineEdit)
        fileNameLayout.addWidget(fileExtensionLabel)

        separateFilesLabel = QLabel("")
        separateFilesLabel.setFixedWidth(110)
        self.separateFilesCB = QCheckBox("separate files")
        separateFilesLayout = QHBoxLayout()
        separateFilesLayout.addWidget(separateFilesLabel)
        separateFilesLayout.addWidget(self.separateFilesCB)

        portFilterLabel = QLabel("Recorded ports")
        portFilterLabel.setFixedWidth(100)
        self.portFilterLineEdit = QLineEdit()
        self.portFilterLineEdit.setPlaceholderText("\"COM1\", \"COMxy\"")
        self.portFilterLineEdit.setToolTip("Empty means all currently connected ports!")
        self.portFilterLineEdit.setToolTip("Empty means all currently connected ports!")
        self.portFilterLineEdit.textChanged.connect(self.portFilterChanged)
        portFilterLayout = QHBoxLayout()
        portFilterLayout.addWidget(portFilterLabel)
        portFilterLayout.addWidget(self.portFilterLineEdit)
        portFilterLayout.addSpacing(66)

        fromLabel = QLabel("From")
        fromLabel.setFixedWidth(140)
        self.fromSpinBox = QSpinBox()
        self.fromSpinBox.setFixedWidth(80)
        self.fromSpinBox.setRange(0, 1000)
        self.fromSpinBox.setValue(30)
        self.fromSpinBox.setSuffix(" °C")
        toLabel = QLabel("To")
        self.toSpinBox = QSpinBox()
        self.toSpinBox.setFixedWidth(80)
        self.toSpinBox.setRange(0, 1000)
        self.toSpinBox.setValue(90)
        self.toSpinBox.setSuffix(" °C")
        fromToLayout = QHBoxLayout()
        fromToLayout.addWidget(fromLabel)
        fromToLayout.addWidget(self.fromSpinBox)
        fromToLayout.addSpacing(20)
        fromToLayout.addWidget(toLabel)
        fromToLayout.addWidget(self.toSpinBox)
        fromToLayout.addStretch()

        inLabel = QLabel("In")
        inLabel.setFixedWidth(140)
        self.inSpinBox = QSpinBox()
        self.inSpinBox.setFixedWidth(80)
        self.inSpinBox.setRange(1, 1000)
        self.inSpinBox.setValue(6)
        stepsLabel = QLabel("steps")
        inStepsLayout = QHBoxLayout()
        inStepsLayout.addWidget(inLabel)
        inStepsLayout.addWidget(self.inSpinBox)
        inStepsLayout.addWidget(stepsLabel)
        inStepsLayout.addStretch()

        hysteresisLabel = QLabel("Hysteresis")
        hysteresisLabel.setFixedWidth(140)
        self.hysteresisCB = QCheckBox()
        self.hysteresisCB.setChecked(True)
        hysteresisLayout = QHBoxLayout()
        hysteresisLayout.addWidget(hysteresisLabel)
        hysteresisLayout.addWidget(self.hysteresisCB)
        hysteresisLayout.addStretch()

        holdTimeLabel = QLabel("Hold time")
        holdTimeLabel.setFixedWidth(140)
        self.holdTimeSpinBox = QSpinBox()
        self.holdTimeSpinBox.setFixedWidth(80)
        self.holdTimeSpinBox.setRange(0, 9999)
        self.holdTimeSpinBox.setValue(60)
        self.holdTimeSpinBox.setSuffix(" s")
        holdTimeLayout = QHBoxLayout()
        holdTimeLayout.addWidget(holdTimeLabel)
        holdTimeLayout.addWidget(self.holdTimeSpinBox)
        holdTimeLayout.addStretch()

        allowedTempDeviationLabel = QLabel("Approach temp diff")
        allowedTempDeviationLabel.setFixedWidth(140)
        self.allowedTempDeviationSpinBox = QDoubleSpinBox()
        self.allowedTempDeviationSpinBox.setFixedWidth(80)
        self.allowedTempDeviationSpinBox.setRange(0, 9999)
        self.allowedTempDeviationSpinBox.setValue(0.1)
        self.allowedTempDeviationSpinBox.setSuffix(" K")
        allowedTempDeviationLayout = QHBoxLayout()
        allowedTempDeviationLayout.addWidget(allowedTempDeviationLabel)
        allowedTempDeviationLayout.addWidget(self.allowedTempDeviationSpinBox)
        allowedTempDeviationLayout.addStretch()

        allowedHoldTempDeviationLabel = QLabel("Hold temp diff")
        allowedHoldTempDeviationLabel.setFixedWidth(140)
        self.allowedHoldTempDeviationSpinBox = QDoubleSpinBox()
        self.allowedHoldTempDeviationSpinBox.setFixedWidth(80)
        self.allowedHoldTempDeviationSpinBox.setRange(0, 9999)
        self.allowedHoldTempDeviationSpinBox.setValue(0.1)
        self.allowedHoldTempDeviationSpinBox.setSuffix(" K")
        allowedHoldTempDeviationLayout = QHBoxLayout()
        allowedHoldTempDeviationLayout.addWidget(allowedHoldTempDeviationLabel)
        allowedHoldTempDeviationLayout.addWidget(self.allowedHoldTempDeviationSpinBox)
        allowedHoldTempDeviationLayout.addStretch()

        measurementsLabel = QLabel("Measurements")
        measurementsLabel.setFixedWidth(140)
        self.measurementsSpinBox = QSpinBox()
        self.measurementsSpinBox.setFixedWidth(80)
        self.measurementsSpinBox.setRange(0, 9999)
        self.measurementsSpinBox.setValue(100)
        measurementsLayout = QHBoxLayout()
        measurementsLayout.addWidget(measurementsLabel)
        measurementsLayout.addWidget(self.measurementsSpinBox)
        measurementsLayout.addStretch()

        saveTypeLabel = QLabel("Save as")
        saveTypeLabel.setFixedWidth(140)
        self.saveTypeComboBox = QComboBox()
        self.saveTypeComboBox.addItems(["value", "raw"])
        saveTypeLayout = QHBoxLayout()
        saveTypeLayout.addWidget(saveTypeLabel)
        saveTypeLayout.addWidget(self.saveTypeComboBox)
        saveTypeLayout.addStretch()

        self.createTablePB = QPushButton("Create table")
        self.createTablePB.setFixedSize(150, 50)
        self.createTablePB.clicked.connect(self.createTable)
        createTableLayout = QHBoxLayout()
        createTableLayout.addStretch()
        createTableLayout.addWidget(self.createTablePB)

        groupBoxLayout = QVBoxLayout()
        groupBoxLayout.addLayout(fromToLayout)
        groupBoxLayout.addLayout(inStepsLayout)
        groupBoxLayout.addLayout(hysteresisLayout)
        groupBoxLayout.addLayout(holdTimeLayout)
        groupBoxLayout.addLayout(allowedTempDeviationLayout)
        groupBoxLayout.addLayout(allowedHoldTempDeviationLayout)
        groupBoxLayout.addLayout(measurementsLayout)
        groupBoxLayout.addLayout(saveTypeLayout)
        groupBoxLayout.addLayout(createTableLayout)

        groupbox = QGroupBox("Measuring procedure")
        groupbox.setLayout(groupBoxLayout)

        scrollLayout = QVBoxLayout()
        scrollLayout.addLayout(fritteusenComPortLayout)
        scrollLayout.addLayout(filePathLayout)
        scrollLayout.addLayout(fileNameLayout)
        scrollLayout.addLayout(separateFilesLayout)
        scrollLayout.addLayout(portFilterLayout)
        scrollLayout.addSpacing(20)
        scrollLayout.addWidget(groupbox)
        scrollLayout.addStretch()

        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(scrollLayout)

        # _____________________Tab Communication____________________
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)

        prefixLELabel = QLabel("{M")

        self.lineEdit = QLineEdit()
        self.lineEdit.textEdited.connect(self.lineEditTextChanged)
        self.lineEdit.returnPressed.connect(self.sendDataFromLineEdit)
        self.lineEdit.setFixedWidth(100)

        suffixLELabel = QLabel("<CR><LF>")

        self.sendLineEditTextPB = QPushButton("Send command")
        self.sendLineEditTextPB.clicked.connect(self.sendDataFromLineEdit)

        lineEditLayout = QHBoxLayout()
        lineEditLayout.addStretch()
        lineEditLayout.addWidget(prefixLELabel)
        lineEditLayout.addWidget(self.lineEdit)
        lineEditLayout.addWidget(suffixLELabel)
        lineEditLayout.addWidget(self.sendLineEditTextPB)

        communicationLayout = QVBoxLayout()
        communicationLayout.addWidget(self.textEdit)
        communicationLayout.addLayout(lineEditLayout)

        lineEditWidget = QWidget()
        lineEditWidget.setLayout(communicationLayout)

        # _____________________Tab Table____________________
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['Temp. setpoint [°C]', 'Temp. hold time [s]', 'Measuring [count]'])
        for i in range(0, self.table.columnCount()):
            self.table.resizeColumnToContents(i)

        self.setTableEditMode(True)

        self.delRowPB = QPushButton("-")
        self.delRowPB.clicked.connect(lambda: self.deleteRow())
        self.addRowPB = QPushButton("+")
        self.addRowPB.clicked.connect(lambda: self.addRow())

        addDeleteRowLayout = QHBoxLayout()
        addDeleteRowLayout.addStretch()
        addDeleteRowLayout.addWidget(self.delRowPB)
        addDeleteRowLayout.addWidget(self.addRowPB)

        self.startPB = QPushButton("Start measuring procedure")
        self.startPB.clicked.connect(self.startStateMachine)
        self.stopPB = QPushButton("Stop measuring procedure")
        self.stopPB.clicked.connect(self.stopStateMachine)
        self.stopPB.setEnabled(False)

        tableTabLayout = QVBoxLayout()
        tableTabLayout.addWidget(self.table)
        tableTabLayout.addLayout(addDeleteRowLayout)
        tableTabLayout.addWidget(self.startPB)
        tableTabLayout.addWidget(self.stopPB)
        tableTabWidget = QWidget()
        tableTabWidget.setLayout(tableTabLayout)

        # _____________________Tab Graph____________________
        self.graphWidget = PlotWidget()
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground(None)
        self.graphWidget.addLegend()

        pen = mkPen(color=QColor(255, 0, 0))
        self.graphLines["Temp"] = GraphLine(self.graphStartTime)
        self.graphLines["Temp"].dataLine = self.graphWidget.plot([], [], pen=pen, name="Temp")

        pen = mkPen(color=QColor(0, 255, 0))
        self.graphLines["SetPoint"] = GraphLine(self.graphStartTime)
        self.graphLines["SetPoint"].dataLine = self.graphWidget.plot([], [], pen=pen, name="Set Point")

        # _____________________Tab Widget____________________
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.scrollWidget, "Settings")
        self.tabWidget.addTab(tableTabWidget, "Table")
        self.tabWidget.addTab(lineEditWidget, "Communication")
        self.tabWidget.addTab(self.graphWidget, "Graph")

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.tabWidget)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def runStateMachine(self, answerReceived: bool = False, answer: str = ""):
        if self.currentState == "idle":
            pass
        elif self.currentState == "setNextTemperature":
            self.setPointTemp = self.getCellValue(self.currentWorkingRow, 0)
            self.setPointHex = self.toHex(self.getCellValue(self.currentWorkingRow, 0)*100)
            if not answerReceived:
                self.sendCommand("71", self.setPointHex, sender="stateMachine", retryCount=2)       # SollTemperatur
            else:
                if answer[2:4] == "71" and answer[4:8] == self.setPointHex:
                    self.setCellStatus(self.currentWorkingRow, 0, status="WORKING")
                    self.setState("startTemperatureControl")
                else:
                    print("FEHLER: setNextTemperature | ", answerReceived, "answer:", answer)
                self.runStateMachineAfterDelay(1000)
        elif self.currentState == "startTemperatureControl":
            if not answerReceived:
                self.sendCommand("14", self.toHex(1), sender="stateMachine", retryCount=2)
            else:
                if answer[2:4] == "14" and answer[4:8] == self.toHex(1):
                    self.setState("checkIfTempReached")
                self.runStateMachineAfterDelay(1000)
        elif self.currentState == "checkIfTempReached":
            if not answerReceived:
                self.sendCommand("01", "****", sender="stateMachine", retryCount=2)
            else:
                if answer[2:4] == "01":
                    self.setCellStatus(self.currentWorkingRow, 0, text=str(self.toDec(answer[4:8])/100) + "/" + str(self.setPointTemp) + " °C", status="WORKING")
                    if abs(self.toDec(answer[4:8])/100 - self.setPointTemp) < self.setPointDiffReached:                                  # SollTemperatur und Abweichung zur Solltemperatur
                        self.tempInBoundsStartTimer = time.time()
                        self.holdTime = self.getCellValue(self.currentWorkingRow, 1)
                        self.setCellStatus(self.currentWorkingRow, 0, text=str(self.setPointTemp) + "/" + str(self.setPointTemp) + " °C", status="DONE")
                        self.setCellStatus(self.currentWorkingRow, 1, status="WORKING")
                        self.setState("checkIfTempInBounds")
                else:
                    print("FEHLER: checkIfTempReached | ", answerReceived, "answer:", answer)
                self.runStateMachineAfterDelay(1000)
        elif self.currentState == "checkIfTempInBounds":
            if not answerReceived:
                self.sendCommand("01", "****", sender="stateMachine", retryCount=2)
            else:
                if answer[2:4] == "01":
                    self.setCellStatus(self.currentWorkingRow, 0, text=str(self.toDec(answer[4:8]) / 100) + "/" + str(self.setPointTemp) + " °C", status="DONE")
                    self.setCellStatus(self.currentWorkingRow, 1, text=str(int(time.time()-self.tempInBoundsStartTimer)) + "/" + str(self.holdTime) + " s", status="WORKING")
                    if abs(self.toDec(answer[4:8])/100 - self.setPointTemp) < self.setPointDiffHold:
                        if time.time() - self.tempInBoundsStartTimer > self.holdTime:                                  # SollTemperatur und Abweichung zur Solltemperatur und Haltezeit
                            for key in self.incomingDataBuffer.keys():
                                self.incomingDataBuffer[key] = []
                            self.requiredDataNumber = self.getCellValue(self.currentWorkingRow, 2)
                            self.gatheredDataCounter = 0
                            self.setCellStatus(self.currentWorkingRow, 1, text=str(self.holdTime) + "/" + str(self.holdTime) + " s", status="DONE")
                            self.setCellStatus(self.currentWorkingRow, 2, status="WORKING")
                            self._separateFileStr = "_" + str(self.currentWorkingRow) if self.separateFilesCB.isChecked() else ""
                            self.setState("measuring")
                    else:
                        self.tempInBoundsStartTimer = time.time()
                else:
                    print("FEHLER: checkIfTempInBounds | ", answerReceived, "answer:", answer)
                self.runStateMachineAfterDelay(1000)
        elif self.currentState == "measuring":
            if not answerReceived:
                self.sendCommand("01", "****", sender="stateMachine", retryCount=2)
            else:
                if answer[2:4] == "01":
                    self.setCellStatus(self.currentWorkingRow, 0, text=str(self.toDec(answer[4:8]) / 100) + "/" + str(self.setPointTemp) + " °C", status="DONE")
                    bufferIsEmpty = False
                    for port in self.portFilter:
                        if port in self.incomingDataBuffer.keys():
                            if len(self.incomingDataBuffer[port]) == 0:
                                bufferIsEmpty = True
                        else:
                            bufferIsEmpty = True
                    if bufferIsEmpty == False:
                        dataList = []
                        headerList = ["Time", "Set temp.", "Actual temp.", "Headers"]
                        if self.portFilter == []:
                            for key in self.incomingDataBuffer.keys():
                                for counter, data in enumerate(self.incomingDataBuffer[key]):
                                    if self.saveTypeComboBox.currentText() == "raw":
                                        dataList.append(data)
                                    else:
                                        dataList.append(str(int(data, 16)))
                                    headerList.append(str(key) + "_" + str(counter))
                                self.incomingDataBuffer[key] = []
                        else:
                            for port in self.portFilter:
                                for counter, data in enumerate(self.incomingDataBuffer[port]):
                                    if self.saveTypeComboBox.currentText() == "raw":
                                        dataList.append(data)
                                    else:
                                        dataList.append(str(int(data, 16)))
                                    headerList.append(str(port) + "_" + str(counter))
                                self.incomingDataBuffer[port] = []
                        # self.saveDataBuffer.append([time.time(), self.toDec(answer[4:8]) / 100, dataList])
                        with open(Path(self.filePath, self.fileName.replace(".txt", "") + self._separateFileStr + ".txt"), 'a') as file:
                            line = str(time.time()) + "\t"
                            line += str(self.setPointTemp) + "\t"
                            line += str(self.toDec(answer[4:8])/100) + "\t"
                            line += "\"[" + ", ".join(headerList) + "]\"\t"
                            line += "\t".join(dataList) + "\n"
                            file.write(line)

                        self.gatheredDataCounter += 1
                        self.setCellStatus(self.currentWorkingRow, 2, text=str(self.gatheredDataCounter) + "/" + str(self.requiredDataNumber), status="WORKING")
                        if self.gatheredDataCounter >= self.requiredDataNumber:
                            self.setCellStatus(self.currentWorkingRow, 2, text=str(self.requiredDataNumber) + "/" + str(self.requiredDataNumber), status="DONE")
                            if self.currentWorkingRow < self.table.rowCount()-1:
                                self.currentWorkingRow += 1
                                self.setState("setNextTemperature")
                            else:
                                print("measuring done!")
                                self.currentWorkingRow = 0
                                self.setState("stopTemperatureControl")
                else:
                    print("FEHLER: measuring | ", answerReceived, "answer:", answer)
                self.runStateMachineAfterDelay(1000)
        elif self.currentState == "stopTemperatureControl":
            if not answerReceived:
                self.sendCommand("14", self.toHex(0), sender="stateMachine", retryCount=5)
            else:
                if answer[2:4] == "14" and answer[4:8] == self.toHex(0):
                    self.setState("idle")
                self.runStateMachineAfterDelay(1000)

    def startStateMachine(self):
        if self.currentState == "idle":
            self.setState("setNextTemperature")
            self.runStateMachine()
        self.setTableEditMode(False)
        self.scrollWidget.setEnabled(False)
        self.delRowPB.setEnabled(False)
        self.addRowPB.setEnabled(False)
        self.startPB.setEnabled(False)
        self.stopPB.setEnabled(True)

    def stopStateMachine(self):
        self.setState("idle")
        self.currentWorkingRow = 0
        self.stateMachineDelayTimer.stop()
        self.setTableEditMode(True)
        self.scrollWidget.setEnabled(True)
        self.delRowPB.setEnabled(True)
        self.addRowPB.setEnabled(True)
        self.startPB.setEnabled(True)
        self.stopPB.setEnabled(False)

    def runStateMachineAfterDelay(self, msec: int = 1000):
        self.stateMachineDelayTimer.start(msec)

    def setState(self, state: str):
        self.lastState = self.currentState
        self.currentState = state

    def lineEditTextChanged(self, text):
        cursorPos = self.lineEdit.cursorPosition()
        self.lineEdit.setText(''.join(x.upper() for x in text if x.upper() in ["*", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]))
        self.lineEdit.setCursorPosition(cursorPos)

    def createTable(self):
        self.filePath = self.showFilePathLabel.text()
        self.fileName = self.fileNameLineEdit.text()
        self.fileName = self.fileName.replace("DATE", datetime.now().strftime("%Y-%m-%d"))
        self.fileName = self.fileName.replace("TIME", datetime.now().strftime("%H-%M-%S"))
        startTemp = self.fromSpinBox.value()
        endTemp = self.toSpinBox.value()
        steps = self.inSpinBox.value()
        hysteresis = self.hysteresisCB.isChecked()
        holdTime = self.holdTimeSpinBox.value()
        self.setPointDiffReached = self.allowedTempDeviationSpinBox.value()
        self.setPointDiffHold = self.allowedHoldTempDeviationSpinBox.value()
        measurements = self.measurementsSpinBox.value()

        while self.table.rowCount() > 0:
            self.deleteRow()

        for i in range(0, steps + 1):
            temp = int(startTemp + (endTemp-startTemp) / steps * i)
            self.addRow(temp, holdTime, measurements)

        if hysteresis:
            for i in range(0, steps + 1):
                temp = int(endTemp - (endTemp - startTemp) / steps * i)
                self.addRow(temp, holdTime, measurements)
        self.setTableEditMode(True)
        self.tabWidget.setCurrentIndex(1)

    def addRow(self, temp: int = 30, holdTime: int = 60, measurementCount: int = 100):
        self.table.setRowCount(self.table.rowCount() + 1)
        tempSpinbox = QSpinBox()
        tempSpinbox.setSuffix(" °C")
        tempSpinbox.setRange(0, 1000)
        tempSpinbox.setValue(temp)
        holdTimeSpinbox = QSpinBox()
        holdTimeSpinbox.setSuffix(" s")
        holdTimeSpinbox.setRange(0, 9999)
        holdTimeSpinbox.setValue(holdTime)
        measurementSpinbox = QSpinBox()
        measurementSpinbox.setRange(0, 9999)
        measurementSpinbox.setValue(measurementCount)

        tempLabel = QLabel("0/" + str(temp) + " °C")
        tempLabel.setAlignment(Qt.AlignHCenter)
        holdTimeLabel = QLabel("0/" + str(holdTime) + " s")
        holdTimeLabel.setAlignment(Qt.AlignHCenter)
        measurementLabel = QLabel("0/" + str(measurementCount))
        measurementLabel.setAlignment(Qt.AlignHCenter)

        tempSpinbox.valueChanged.connect(lambda value: tempLabel.setText("0/" + str(value) + " °C"))
        holdTimeSpinbox.valueChanged.connect(lambda value: holdTimeLabel.setText("0/" + str(value) + " s"))
        measurementSpinbox.valueChanged.connect(lambda value: measurementLabel.setText("0/" + str(value)))

        tempLayout = QHBoxLayout()
        tempLayout.addStretch()
        tempLayout.addWidget(tempSpinbox)
        tempLayout.addWidget(tempLabel)
        tempLayout.addStretch()
        holdTimeLayout = QHBoxLayout()
        holdTimeLayout.addStretch()
        holdTimeLayout.addWidget(holdTimeSpinbox)
        holdTimeLayout.addWidget(holdTimeLabel)
        holdTimeLayout.addStretch()
        measurementLayout = QHBoxLayout()
        measurementLayout.addStretch()
        measurementLayout.addWidget(measurementSpinbox)
        measurementLayout.addWidget(measurementLabel)
        measurementLayout.addStretch()

        tempWidget = QWidget()
        tempWidget.setLayout(tempLayout)
        holdTimeWidget = QWidget()
        holdTimeWidget.setLayout(holdTimeLayout)
        measurementWidget = QWidget()
        measurementWidget.setLayout(measurementLayout)

        self.table.setCellWidget(self.table.rowCount() - 1, 0, tempWidget)
        self.table.setCellWidget(self.table.rowCount() - 1, 1, holdTimeWidget)
        self.table.setCellWidget(self.table.rowCount() - 1, 2, measurementWidget)

        for i in range(0, self.table.rowCount()):
            self.table.resizeRowToContents(i)
        self.setTableEditMode(True)

    def deleteRow(self):
        if self.table.rowCount() > 0:
            self.table.setRowCount(self.table.rowCount() - 1)
        self.setTableEditMode(True)

    def setTableEditMode(self, b: bool = False):
        if b == True:
            for row in range(0, self.table.rowCount()):
                self.setCellStatus(row, 0, status="NOTDONE")
                self.setCellStatus(row, 1, status="NOTDONE")
                self.setCellStatus(row, 2, status="NOTDONE")
                self.table.cellWidget(row, 0).layout().itemAt(1).widget().show()
                self.table.cellWidget(row, 0).layout().itemAt(2).widget().hide()
                self.table.cellWidget(row, 1).layout().itemAt(1).widget().show()
                self.table.cellWidget(row, 1).layout().itemAt(2).widget().hide()
                self.table.cellWidget(row, 2).layout().itemAt(1).widget().show()
                self.table.cellWidget(row, 2).layout().itemAt(2).widget().hide()
        else:
            for row in range(0, self.table.rowCount()):
                self.table.cellWidget(row, 0).layout().itemAt(1).widget().hide()
                self.table.cellWidget(row, 0).layout().itemAt(2).widget().show()
                self.table.cellWidget(row, 1).layout().itemAt(1).widget().hide()
                self.table.cellWidget(row, 1).layout().itemAt(2).widget().show()
                self.table.cellWidget(row, 2).layout().itemAt(1).widget().hide()
                self.table.cellWidget(row, 2).layout().itemAt(2).widget().show()

    def setCellStatus(self, row: int, column: int, text: str = "", status: str = "NOTDONE"):
        cellWidget = self.table.cellWidget(row, column).layout().itemAt(2).widget()
        if text != "":
            cellWidget.setText(text)
        if status == "NOTDONE":
            self.table.cellWidget(row, column).setStyleSheet("background-color: transparent")
        if status == "WORKING":
            self.table.cellWidget(row, column).setStyleSheet("QWidget{background-color: rgba(150, 150, 0, 100)}QLabel{background-color: transparent}QSpinBox{background-color: rgba(0, 0, 0, 20)}")
        if status == "DONE":
            self.table.cellWidget(row, column).setStyleSheet("QWidget{background-color: rgba(0, 100, 0, 100)}QLabel{background-color: transparent}QSpinBox{background-color: rgba(0, 0, 0, 20)}")

    def getCellValue(self, row: int, column: int):
        return self.table.cellWidget(row, column).layout().itemAt(1).widget().value()

    def askForTemp(self):
        if len(self.commMessageBacklog) == 0:
            self.sendCommand("01", "****", sender="askForTemp")

    def portFilterChanged(self):
        text = self.portFilterLineEdit.text().replace("[", "").replace("]", "").replace(";", ",").replace("/", ",")
        self.portFilter = []
        for port in text.split(","):
            self.portFilter.append(port.strip().upper())

    def openFilePathButtonPressed(self, port):
        path = QFileDialog.getExistingDirectory(None, "Select Folder", "", QFileDialog.DontUseNativeDialog | QFileDialog.ShowDirsOnly)
        self.checkForValidSavePath(path)

    def checkForValidSavePath(self, path):
        if path and os.path.isdir(path):
            self.showFilePathLabel.setText(str(path))
            self.showFilePathLabel.adjustSize()

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        if serialParameters.readTextIndex == "read_line" and dataInfo["dataType"] == "RAW-Values" and type(data) == bytes:
            data = data.decode()
            if re.match(r"\{S[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]", data):
                if self.fritteusenComPortLineEdit.text() == "":
                    self.fritteusenComPortLineEdit.setText(serialParameters.port)
                self.receiveCalibratorAnswer(data.strip())
        if serialParameters.readTextIndex == "read_WU_device" and dataInfo["dataType"] == "RAW-Values":
            self.incomingDataBuffer[serialParameters.port.upper()] = data

    def receiveCalibratorAnswer(self, message: str, serialParameters: SerialParameters = None, dataInfo = None):
        self.waitforAnswerTimer.stop()
        self.isActiveCommunication = False
        addess = message[2:4]
        value = self.toDec(message[4:8])

        # ____________Write to textEdit__________________
        self.textEdit.setPlainText(self.textEdit.toPlainText() + message[0:2] + " " + message[2:4] + " " + message[4:8])
        if addess in self.addressDict.keys():
            self.textEdit.setPlainText(self.textEdit.toPlainText() + "    | " + self.addressDict[addess][0].ljust(10) + " [" + self.addressDict[addess][1] + "]: " + str(value))
            if self.addressDict[addess][2] != "":
                self.textEdit.setPlainText(self.textEdit.toPlainText() + " * " + self.addressDict[addess][2])
        self.textEdit.append("")
        self.textEdit.moveCursor(QTextCursor.End)

        # ____________Append to graph__________________
        if len(self.currentCommMassage) > 0 and addess == "01" and self.currentCommMassage[3] == "askForTemp":
            self.graphLines["SetPoint"].appendDataPoint(self.setPointTemp)
            self.graphLines["Temp"].appendDataPoint(value/100)
        elif addess == "71" and self.currentCommMassage[3] == "askForTemp":
            self.graphLines["SetPoint"].appendDataPoint(self.setPointTemp)

        # ____________Run state machine__________________
        if len(self.currentCommMassage) > 0 and self.currentCommMassage[3] == "stateMachine":
            self.runStateMachine(True, message)
        if len(self.commMessageBacklog) > 0:
            c = self.commMessageBacklog.pop(0)
            self.sendCommand(c[0], c[1], c[2], c[3], c[4])

    def noAnswerReceived(self):
        self.textEdit.setPlainText(self.textEdit.toPlainText() + ".....")
        self.textEdit.append("")
        self.textEdit.moveCursor(QTextCursor.End)

        self.isActiveCommunication = False
        if self.currentCommMassage[4] > 0:
            self.currentCommMassage[4] = self.currentCommMassage[4] - 1
            self.sendCommand(self.currentCommMassage[0], self.currentCommMassage[1], self.currentCommMassage[2], self.currentCommMassage[3], self.currentCommMassage[4])
            return
        if self.currentCommMassage[3] == "stateMachine":
            self.runStateMachine(False)
        if len(self.commMessageBacklog) > 0:
            c = self.commMessageBacklog.pop(0)
            self.sendCommand(c[0], c[1], c[2], c[3], c[4])

    def sendDataFromLineEdit(self):
        self.sendCommand(self.lineEdit.text(), "", sender="lineEdit", retryCount=5)

    def sendCommand(self, address: str, value=None, timeout: int = 1000, sender: str = "", retryCount: int = 0):
        if self.isActiveCommunication == True:
            if len(self.commMessageBacklog) < self.maxCommBacklogSize or sender == "stateMachine":
                self.commMessageBacklog.append([address, value, timeout, sender, retryCount])
            return

        if value == None:
            value = "****"
        elif type(value) == int:
            value = self.toHex(value)

        self.isActiveCommunication = True
        self.waitforAnswerTimer.start(timeout)
        #self.textEdit.setPlainText(self.textEdit.toPlainText() + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " | ")
        plainText = self.textEdit.toPlainText()
        if len(plainText) > 6000:
            self.textEdit.setPlainText(plainText[-5000:])
        self.textEdit.setPlainText(self.textEdit.toPlainText() + "{M " + address + " " + str(value) + "   -->   ")
        self.textEdit.moveCursor(QTextCursor.End)
        self.currentCommMassage = [address, value, timeout, sender, retryCount]
        self.sendData("{M" + address + str(value) + "\r\n")

    def sendData(self, data):
        if self.fritteusenComPortLineEdit.text() == "":
            self.sendSerialData(data.encode('utf-8'))
        else:
            self.sendSerialData(data.encode('utf-8'), [self.fritteusenComPortLineEdit.text()])

    def toHex(self, decValue: int):
        return format(decValue, 'x').upper().zfill(4)

    def toDec(self, hexValue: str):
        return int(hexValue, 16)

    def save(self):
        saveDict = {
            "fritteusenComPort": self.fritteusenComPortLineEdit.text(),
            "filePath": self.showFilePathLabel.text(),
            "fileName": self.fileNameLineEdit.text(),
            "separateFiles": self.separateFilesCB.isChecked(),
            "recordedPorts": self.portFilterLineEdit.text(),
            "fromSB": self.fromSpinBox.value(),
            "toSB": self.toSpinBox.value(),
            "inSB": self.inSpinBox.value(),
            "hysteresisCB": self.hysteresisCB.isChecked(),
            "holdTimeSB": self.holdTimeSpinBox.value(),
            "tempDivSB": self.allowedTempDeviationSpinBox.value(),
            "holdTempDivSB": self.allowedHoldTempDeviationSpinBox.value(),
            "measurementsSB": self.measurementsSpinBox.value(),
            "saveType": self.saveTypeComboBox.currentText()
        }
        return saveDict

    def load(self, data):
        self.fritteusenComPortLineEdit.setText(data["fritteusenComPort"])
        self.checkForValidSavePath(data["filePath"])
        self.fileNameLineEdit.setText(data["fileName"])
        self.separateFilesCB.setChecked(data["separateFiles"])
        self.portFilterLineEdit.setText(data["recordedPorts"])
        self.fromSpinBox.setValue(data["fromSB"])
        self.toSpinBox.setValue(data["toSB"])
        self.inSpinBox.setValue(data["inSB"])
        self.hysteresisCB.setChecked(data["hysteresisCB"])
        self.holdTimeSpinBox.setValue(data["holdTimeSB"])
        self.allowedTempDeviationSpinBox.setValue(data["tempDivSB"])
        self.allowedHoldTempDeviationSpinBox.setValue(data["holdTempDivSB"])
        self.measurementsSpinBox.setValue(data["measurementsSB"])
        self.saveTypeComboBox.setCurrentText(data["saveType"])

