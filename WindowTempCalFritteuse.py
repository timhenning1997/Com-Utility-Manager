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
from DeviceCommunication.CalibratorFritteuse import CalibratorFritteuse
from DeviceCommunication.Keithley2010 import Keithley2010


class GraphLine:
    def __init__(self):
        self.dataLine = None

    def setDataPoints(self, x: list, y: list):
        self.dataLine.setData(x, y)


class WindowTempCalFritoese(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "TempCalFritteuse")

        self.cal = CalibratorFritteuse(self, "")
        self.keithley = Keithley2010(self, "")

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

        self.stateMachineDelayTimer = QTimer(self)
        self.stateMachineDelayTimer.timeout.connect(self.runStateMachine)
        self.stateMachineDelayTimer.setSingleShot(True)

        self.askForCurrentTempTimer = QTimer(self)
        self.askForCurrentTempTimer.timeout.connect(self.cal.askForTemp)
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
        self.fritteusenComPortLineEdit.textChanged.connect(self.portFilterChanged)
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

        # _____________Additional Devices______________
        self.keithleyUseCB = QCheckBox("Keithley")
        self.keithleyUseCB.setFixedWidth(100)
        self.keithleyUseCB.clicked.connect(self.keithleyUseButtonPressed)
        self.keithleyComPortLabel = QLabel("Keithley COM")
        self.keithleyComPortLabel.setFixedWidth(100)
        self.keithleyComPortLabel.setVisible(False)
        self.keithleyComPortLineEdit = QLineEdit("")
        self.keithleyComPortLineEdit.setPlaceholderText("COMXY")
        self.keithleyComPortLineEdit.setFixedWidth(60)
        self.keithleyComPortLineEdit.textChanged.connect(self.portFilterChanged)
        self.keithleyComPortLineEdit.setVisible(False)
        keithleyComPortLayout = QHBoxLayout()
        keithleyComPortLayout.addWidget(self.keithleyComPortLabel)
        keithleyComPortLayout.addWidget(self.keithleyComPortLineEdit)
        keithleyComPortLayout.addStretch()

        self.keithleyTable = QTableWidget(0, 4)
        self.keithleyTable.setHorizontalHeaderLabels(["Name", "Channel", "Function", "Range"])
        self.addKeithleyRow()

        self.addRowButton = QPushButton("+ Row")
        self.addRowButton.clicked.connect(self.addKeithleyRow)
        self.deleteRowButton = QPushButton("- Row")
        self.deleteRowButton.clicked.connect(self.deleteLastKeithleyRow)
        keithleyAddDelLayout = QHBoxLayout()
        keithleyAddDelLayout.addStretch()
        keithleyAddDelLayout.addWidget(self.addRowButton)
        keithleyAddDelLayout.addWidget(self.deleteRowButton)

        additionalDevicesGroupBoxLayout = QVBoxLayout()
        additionalDevicesGroupBoxLayout.addWidget(self.keithleyUseCB)
        additionalDevicesGroupBoxLayout.addLayout(keithleyComPortLayout)
        additionalDevicesGroupBoxLayout.addWidget(self.keithleyTable)
        additionalDevicesGroupBoxLayout.addLayout(keithleyAddDelLayout)

        additionalDevicesGroupbox = QGroupBox("Additional devices")
        additionalDevicesGroupbox.setLayout(additionalDevicesGroupBoxLayout)

        scrollLayout = QVBoxLayout()
        scrollLayout.addLayout(fritteusenComPortLayout)
        scrollLayout.addLayout(filePathLayout)
        scrollLayout.addLayout(fileNameLayout)
        scrollLayout.addLayout(separateFilesLayout)
        scrollLayout.addLayout(portFilterLayout)
        scrollLayout.addSpacing(20)
        scrollLayout.addWidget(additionalDevicesGroupbox)
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
        self.graphLines["Temp"] = GraphLine()
        self.graphLines["Temp"].dataLine = self.graphWidget.plot([], [], pen=pen, name="Temp")

        pen = mkPen(color=QColor(0, 255, 0))
        self.graphLines["SetPoint"] = GraphLine()
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
            if self.cal.newSetPointAvailable:
                self.cal.newSetPointAvailable = False

                self.setPointTemp = self.getCellValue(self.currentWorkingRow, 0)
                if self.cal.lastSetPointTemp == self.setPointTemp:
                    self.setCellStatus(self.currentWorkingRow, 0, status="WORKING")
                    if self.keithleyUseCB.isChecked():
                        self.setState("initKeithley")
                    else:
                        self.setState("startTemperatureControl")
                    self.cal.newTempControlAvailable = False
            else:
                self.cal.setSetPointTemp(self.setPointTemp)
        elif self.currentState == "initKeithley":
            if self.keithley.isInitDone:
                self.keithley.isInitDone = False
                self.setState("startTemperatureControl")
            else:
                self.keithley.initKeithley()
        elif self.currentState == "startTemperatureControl":
            if self.cal.newTempControlAvailable:
                self.cal.newTempControlAvailable = False

                if self.cal.isTempControlActive == True:
                    self.setState("checkIfTempReached")
                    self.cal.newTempAvailable = False
            else:
                self.cal.setTempControl(True)
        elif self.currentState == "checkIfTempReached":
            if self.cal.newTempAvailable:
                self.cal.newTempAvailable = False

                self.setCellStatus(self.currentWorkingRow, 0, text=str(self.cal.lastTempValue) + "/" + str(self.setPointTemp) + " °C", status="WORKING")
                if abs(self.cal.lastTempValue - self.setPointTemp) < self.setPointDiffReached:
                    self.tempInBoundsStartTimer = time.time()
                    self.holdTime = self.getCellValue(self.currentWorkingRow, 1)
                    self.setCellStatus(self.currentWorkingRow, 0, text=str(self.setPointTemp) + "/" + str(self.setPointTemp) + " °C", status="DONE")
                    self.setCellStatus(self.currentWorkingRow, 1, status="WORKING")
                    self.setState("checkIfTempInBounds")
            else:
                self.cal.askForTemp()
        elif self.currentState == "checkIfTempInBounds":
            if self.cal.newTempAvailable:
                self.cal.newTempAvailable = False

                self.setCellStatus(self.currentWorkingRow, 0, text=str(self.cal.lastTempValue) + "/" + str(self.setPointTemp) + " °C", status="DONE")
                self.setCellStatus(self.currentWorkingRow, 1, text=str(int(time.time()-self.tempInBoundsStartTimer)) + "/" + str(self.holdTime) + " s", status="WORKING")
                if abs(self.cal.lastTempValue - self.setPointTemp) < self.setPointDiffHold:
                    if time.time() - self.tempInBoundsStartTimer > self.holdTime:
                        self.requiredDataNumber = self.getCellValue(self.currentWorkingRow, 2)
                        self.gatheredDataCounter = 0
                        self.setCellStatus(self.currentWorkingRow, 1, text=str(self.holdTime) + "/" + str(self.holdTime) + " s", status="DONE")
                        self.setCellStatus(self.currentWorkingRow, 2, status="WORKING")
                        self._separateFileStr = "_" + str(self.currentWorkingRow) if self.separateFilesCB.isChecked() else ""
                        self.setState("measuring")
                else:
                    self.tempInBoundsStartTimer = time.time()
            else:
                self.cal.askForTemp()
        elif self.currentState == "measuring":
            if self.cal.newTempAvailable and (not self.keithleyUseCB.isChecked() or self.keithley.newKeithleyAvailable):
                self.cal.newTempAvailable = False
                self.keithley.newKeithleyAvailable = False

                self.setCellStatus(self.currentWorkingRow, 0, text=str(self.cal.lastTempValue) + "/" + str(self.setPointTemp) + " °C", status="DONE")
                bufferIsEmpty = False
                for port in self.portFilter:
                    if port in self.incomingDataBuffer.keys():
                        if len(self.incomingDataBuffer[port]) == 0:
                            bufferIsEmpty = True
                    else:
                        bufferIsEmpty = True
                if bufferIsEmpty == False:
                    dataList = []
                    headerList = ["Time", "Unix Time", "Set temp.", "Actual temp."]
                    if self.keithleyUseCB.isChecked():
                        for name in self.getKeithleyColumn(0):
                            headerList.append(name)
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
                    with open(Path(self.filePath, self.fileName.replace(".txt", "") + self._separateFileStr + ".txt"), 'a') as file:
                        line = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "\t"
                        line += str(time.time()) + "\t"
                        line += str(self.setPointTemp) + "\t"
                        line += str(self.cal.lastTempValue)
                        if self.keithleyUseCB.isChecked():
                            s = []
                            for val in self.keithley.lastKeithleyValues:
                                s.append(str(val))
                            line += "\t" + "\t".join(s)
                        if len(dataList) > 0:
                            line += "\t" + "\t".join(dataList)
                        line += "\n"
                        file.write(line)
                    self.gatheredDataCounter += 1
                    self.setCellStatus(self.currentWorkingRow, 2, text=str(self.gatheredDataCounter) + "/" + str(self.requiredDataNumber), status="WORKING")

                if self.gatheredDataCounter >= self.requiredDataNumber:
                    self.setCellStatus(self.currentWorkingRow, 2, text=str(self.requiredDataNumber) + "/" + str(self.requiredDataNumber), status="DONE")
                    if self.currentWorkingRow < self.table.rowCount()-1:
                        if self.separateFilesCB.isChecked():
                            with open(Path(self.filePath, self.fileName.replace(".txt", "") + self._separateFileStr + ".txt"), 'r+') as file:
                                content = file.read()
                                file.seek(0, 0)
                                file.write("\t".join(headerList) + "\n" + content)
                        self.currentWorkingRow += 1
                        self.setState("setNextTemperature")
                        self.cal.newSetPointAvailable = False
                    else:
                        with open(Path(self.filePath, self.fileName.replace(".txt", "") + self._separateFileStr + ".txt"), 'r+') as file:
                            content = file.read()
                            file.seek(0, 0)
                            file.write("\t".join(headerList) + "\n" + content)
                        self.currentWorkingRow = 0
                        self.setState("stopTemperatureControl")
                        self.cal.newTempControlAvailable = False
            else:
                self.cal.askForTemp()
                if self.keithleyUseCB.isChecked():
                    self.keithley.askForKeithley(self.getKeithleyColumn(1), self.getKeithleyColumn(2), self.getKeithleyColumn(3))
        elif self.currentState == "stopTemperatureControl":
            if self.cal.newTempControlAvailable:
                self.cal.newTempControlAvailable = False

                if self.cal.isTempControlActive == False:
                    self.setState("idle")
                    self.cal.newTempAvailable = False
                    self.cal.newTempControlAvailable = False
                    self.cal.newSetPointAvailable = False
                    return
            else:
                self.cal.setTempControl(True)

        self.runStateMachineAfterDelay(300)

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

    def addKeithleyRow(self):
        self.keithleyTable.setRowCount(self.keithleyTable.rowCount() + 1)
        self.keithleyTable.setCellWidget(self.keithleyTable.rowCount() - 1, 0, QLineEdit("Name" + str(self.keithleyTable.rowCount())))
        channelSpinbox = QSpinBox()
        channelSpinbox.setRange(0, 100000)
        self.keithleyTable.setCellWidget(self.keithleyTable.rowCount() - 1, 1, channelSpinbox)
        funcComboBox = QComboBox()
        funcComboBox.addItem("VOLT:DC")
        funcComboBox.addItem("VOLT:AC")
        funcComboBox.addItem("CURR:DC")
        funcComboBox.addItem("CURR:AC")
        funcComboBox.addItem("RES")
        funcComboBox.addItem("FRES")
        funcComboBox.addItem("TEMP")
        self.keithleyTable.setCellWidget(self.keithleyTable.rowCount() - 1, 2, funcComboBox)
        rangeSpinbox = QSpinBox()
        rangeSpinbox.setRange(0, 100000)
        self.keithleyTable.setCellWidget(self.keithleyTable.rowCount() - 1, 3, rangeSpinbox)

    def deleteLastKeithleyRow(self):
        if self.keithleyTable.rowCount() > 1:
            self.keithleyTable.setRowCount(self.keithleyTable.rowCount() - 1)

    def getKeithleyColumn(self, index: int):
        data = []
        for i in range(0, self.keithleyTable.rowCount()):
            if index == 0:
                data.append(self.keithleyTable.cellWidget(i, index).text())
            elif index == 2:
                data.append(self.keithleyTable.cellWidget(i, index).currentText())
            else:
                data.append(self.keithleyTable.cellWidget(i, index).value())
        return data

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

    def portFilterChanged(self):
        text = self.portFilterLineEdit.text().replace("[", "").replace("]", "").replace(";", ",").replace("/", ",")
        self.portFilter = []
        for port in text.split(","):
            if port != "":
                self.portFilter.append(port.strip().upper())

        text = self.keithleyComPortLineEdit.text().replace("[", "").replace("]", "").replace(";", ",").replace("/", ",")
        port = text.split(",")[0]
        self.keithley._port = port

        text = self.fritteusenComPortLineEdit.text().replace("[", "").replace("]", "").replace(";", ",").replace("/", ",")
        port = text.split(",")[0]
        self.cal._port = port

    def openFilePathButtonPressed(self, port):
        path = QFileDialog.getExistingDirectory(None, "Select Folder", "", QFileDialog.DontUseNativeDialog | QFileDialog.ShowDirsOnly)
        self.checkForValidSavePath(path)

    def checkForValidSavePath(self, path):
        if path and os.path.isdir(path):
            self.showFilePathLabel.setText(str(path))
            self.showFilePathLabel.adjustSize()

    def keithleyUseButtonPressed(self, b: bool):
        self.keithleyComPortLabel.setVisible(b)
        self.keithleyComPortLineEdit.setVisible(b)
        self.keithleyTable.setVisible(b)
        self.addRowButton.setVisible(b)
        self.deleteRowButton.setVisible(b)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        if serialParameters.readTextIndex == "read_line" and dataInfo["dataType"] == "RAW-Values" and type(data) == bytes:
            self.cal.receiveData(serialParameters, data, dataInfo)
            self.graphLines["Temp"].setDataPoints(self.cal.temperatureValues["times"], self.cal.temperatureValues["values"])
            self.graphLines["SetPoint"].setDataPoints(self.cal.setPointTemps["times"], self.cal.setPointTemps["values"])

        if serialParameters.readTextIndex == "read_line" and dataInfo["dataType"] == "RAW-Values":
            self.keithley.receiveData(serialParameters, data, dataInfo)

        if serialParameters.readTextIndex == "read_line" and dataInfo["dataType"] == "RAW-Values" and type(data) == bytes:
            if re.match(r"\{S[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]", data.decode()):
                if self.fritteusenComPortLineEdit.text() == "":
                    self.fritteusenComPortLineEdit.setText(serialParameters.port)
                plainText = self.textEdit.toPlainText()
                if len(plainText) > 1000:
                    self.textEdit.setPlainText(plainText[-600:])
                self.textEdit.setPlainText(self.textEdit.toPlainText() + data.decode().strip())
                self.textEdit.append("")
                self.textEdit.moveCursor(QTextCursor.End)

        if serialParameters.readTextIndex == "read_WU_device" and dataInfo["dataType"] == "RAW-Values":
            self.incomingDataBuffer[serialParameters.port.upper()] = data



    def sendDataFromLineEdit(self):
        self.cal.sendMessage("{M" + self.lineEdit.text() + "\r\n")

    def save(self):
        keithleyTableData = []
        for y in range(0, self.keithleyTable.rowCount()):
            rowData = [self.keithleyTable.cellWidget(y, 0).text(),
                       self.keithleyTable.cellWidget(y, 1).value(),
                       self.keithleyTable.cellWidget(y, 2).currentText(),
                       self.keithleyTable.cellWidget(y, 3).value()]
            keithleyTableData.append(rowData)

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
            "saveType": self.saveTypeComboBox.currentText(),
            "keithleyUseCB": self.keithleyUseCB.isChecked(),
            "keithleyComPort": self.keithleyComPortLineEdit.text(),
            "keithleyTableData": keithleyTableData
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
        self.keithleyUseCB.setChecked(data["keithleyUseCB"])
        self.keithleyUseButtonPressed(self.keithleyUseCB.isChecked())
        self.keithleyComPortLineEdit.setText(data["keithleyComPort"])
        self.portFilterChanged()

        self.keithleyTable.setRowCount(0)
        for row in data["keithleyTableData"]:
            self.addKeithleyRow()
            self.keithleyTable.cellWidget(self.keithleyTable.rowCount()-1, 0).setText(row[0])
            self.keithleyTable.cellWidget(self.keithleyTable.rowCount()-1, 1).setValue(row[1])
            self.keithleyTable.cellWidget(self.keithleyTable.rowCount()-1, 2).setCurrentText(row[2])
            self.keithleyTable.cellWidget(self.keithleyTable.rowCount()-1, 3).setValue(row[3])

