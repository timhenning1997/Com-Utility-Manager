import json
import os
import sys
import csv
from pathlib import Path

from CalibrationFunctions import applyCalibrationFunctions
from collections import OrderedDict
from datetime import datetime

from PyQt5.QtCore import QThreadPool, pyqtSignal, Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QPushButton, QAction, QApplication, QFileDialog, QMenu, QTableWidget, \
    QHBoxLayout, QWidget, QHeaderView, QTableWidgetItem, QMessageBox, QTextEdit, QLineEdit, QVBoxLayout, QSplitter, \
    QLabel, QScrollArea
from HelperWindows import MeasuringPointListWindow, ScrollableLabelWindow
from PortMenu import PortMenu
from SerialConnectWindow import SerialConnectWindow
from SerialWorker import SerialThread
from SerialParameters import SerialParameters
from UsefulFunctions import resource_path, strToIntElseNone, strToFloatElseNone
from AbstractWindow import AbstractWindow
from WindowTerminal import WindowTerminal
from WindowTablePlotter import WindowTablePlotter
from WindowNodeEditor import WindowNodeEditor
from WindowSimpleGraph import WindowSimpleGraph
from WindowRawDataGraph import WindowRawDataGraph
from WindowBetriebsmesstechnik import WindowBetriebsmesstechnik
from WindowTeleTableView import WindowTeleTableView
from WindowSynthetischeDaten import WindowSynthetischeDaten
from WindowTempCalFritteuse import WindowTempCalFritoese
from WindowStationaritaet import WindowStationaritaet
from WindowProgrammer import WindowProgrammer
from WindowTest import WindowTest


class ConnectionHubWindow(QMainWindow):
    sendSerialWriteSignal = pyqtSignal(str, object)
    killSerialConnectionSignal = pyqtSignal(str)
    pauseSerialConnectionSignal = pyqtSignal(str)
    resumeSerialConnectionSignal = pyqtSignal(str)
    startSerialRecordSignal = pyqtSignal(str, str, str)
    stopSerialRecordSignal = pyqtSignal(str)
    pauseSerialRecordSignal = pyqtSignal(str)
    resumeSerialRecordSignal = pyqtSignal(str)
    writeToFileSignal = pyqtSignal(str, str, str, str)

    madeSerialConnectionSignal = pyqtSignal(object)
    lostSerialConnectionSignal = pyqtSignal(object)
    receiveSerialDataSignal = pyqtSignal(object, object)
    receiveCalibratedSerialDataSignal = pyqtSignal(object, object, object)
    failedSendSerialDataSignal = pyqtSignal(object, object)
    startedSerialRecordingSignal = pyqtSignal(object)
    stoppedSerialRecordingSignal = pyqtSignal(object)
    globalVarsChangedSignal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

        self.windows = []
        self.connectedPorts = []
        self.calibrationFiles = {}
        self.measuringPointListFiles = []
        self.globalVars = {}

        self._windowType = "Hub"

        self.initUI()
        self.initSignalsAndSlots()

        if os.path.exists(str(Path(os.getcwd() + "/last_save.json"))):
            self.loadFromFile(str(Path(os.getcwd() + "/last_save.json")))

        self.show()

    def initUI(self):
        self.setWindowTitle("Com Utility Manager")
        self.resize(800, 400)

        self.createMenus()
        self.createStatusBar()

        # create com port table
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(
            ["Del", "COM", "Baud", "Type", "Status", "Record", "Rec", "Rec Name", "Cal"])
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 20)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(6, 20)
        self.table.setColumnWidth(7, 80)
        self.table.setColumnWidth(8, 20)
        self.table.hideColumn(0)
        self.table.hideColumn(7)

        # create Messstellen table
        self.measuringPointListTable = QTableWidget(0, 1)
        self.measuringPointListTable.setHorizontalHeaderLabels(["Measuring point list"])
        self.measuringPointListTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.measuringPointListTable.hide()

        tableSplitter = QSplitter(Qt.Vertical)
        tableSplitter.addWidget(self.table)
        tableSplitter.addWidget(self.measuringPointListTable)
        tableSplitter.setSizes([1000, 200])

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tableSplitter)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

        self.setCentralWidget(mainWidget)

    def initSignalsAndSlots(self):
        self.madeSerialConnectionSignal.connect(self.printMadeConnection)
        self.lostSerialConnectionSignal.connect(self.printLostConnection)
        self.receiveSerialDataSignal.connect(self.printReceivedData)
        self.failedSendSerialDataSignal.connect(self.printFailedSendData)
        self.startedSerialRecordingSignal.connect(self.printStartRecording)
        self.stoppedSerialRecordingSignal.connect(self.printStopRecording)

    def createStatusBar(self):
        self.statusBar().showMessage("")

    def createMenus(self):
        portMenu = PortMenu(self.connectedPorts, self)
        portMenu.connectActionTriggeredSignal.connect(self.openSerialConnectWindow)
        portMenu.disconnectActionTriggeredSignal.connect(self.killSerialConnection)

        fileMenu = QMenu("&File", self)
        actSaveAs = QAction('&Save layout', self, triggered=self.onFileSaveAs)
        actOpen = QAction('&Open layout', self, triggered=self.onFileOpen)
        actMeasurementListOpen = QAction('Open &Measurement list', self, triggered=self.onMeasurementListOpen)
        actGlobalVarsOpen = QAction('Open &Global variables', self, triggered=self.onGlobalVarsOpen)
        actGlobalVarsShow = QAction('Show Global &variables', self, triggered=self.showGlobalVars)
        fileMenu.addAction(actSaveAs)
        fileMenu.addAction(actOpen)
        fileMenu.addAction(actMeasurementListOpen)
        fileMenu.addAction(actGlobalVarsOpen)
        fileMenu.addAction(actGlobalVarsShow)

        tableMenu = QMenu("&Table", self)
        act = QAction("Show/Hide Columns", self)
        act.setEnabled(False)
        font1 = QFont()
        font1.setUnderline(True)
        act.setFont(font1)
        tableMenu.addAction(act)
        self.actShowDelete = QAction('&Delete', self, triggered=lambda obj: self.tableShowColumn(0, obj))
        self.actShowDelete.setCheckable(True)
        self.actShowDelete.setChecked(False)
        self.actShowCom = QAction('&Com', self, triggered=lambda obj: self.tableShowColumn(1, obj))
        self.actShowCom.setCheckable(True)
        self.actShowCom.setChecked(True)
        self.actShowBaud = QAction('&Baud', self, triggered=lambda obj: self.tableShowColumn(2, obj))
        self.actShowBaud.setCheckable(True)
        self.actShowBaud.setChecked(True)
        self.actShowType = QAction('&Type', self, triggered=lambda obj: self.tableShowColumn(3, obj))
        self.actShowType.setCheckable(True)
        self.actShowType.setChecked(True)
        self.actShowStatus = QAction('&Status', self, triggered=lambda obj: self.tableShowColumn(4, obj))
        self.actShowStatus.setCheckable(True)
        self.actShowStatus.setChecked(True)
        self.actShowRecord = QAction('&Record', self, triggered=lambda obj: self.tableShowColumn(5, obj))
        self.actShowRecord.setCheckable(True)
        self.actShowRecord.setChecked(True)
        self.actShowPath = QAction('&Path', self, triggered=lambda obj: self.tableShowColumn(6, obj))
        self.actShowPath.setCheckable(True)
        self.actShowPath.setChecked(True)
        self.actShowRecordName = QAction('Record &Name', self, triggered=lambda obj: self.tableShowColumn(7, obj))
        self.actShowRecordName.setCheckable(True)
        self.actShowRecordName.setChecked(False)
        self.actShowCalibration = QAction('C&alibration', self, triggered=lambda obj: self.tableShowColumn(8, obj))
        self.actShowCalibration.setCheckable(True)
        self.actShowCalibration.setChecked(True)
        tableMenu.addAction(self.actShowDelete)
        tableMenu.addAction(self.actShowCom)
        tableMenu.addAction(self.actShowBaud)
        tableMenu.addAction(self.actShowType)
        tableMenu.addAction(self.actShowStatus)
        tableMenu.addAction(self.actShowRecord)
        tableMenu.addAction(self.actShowPath)
        tableMenu.addAction(self.actShowRecordName)
        tableMenu.addAction(self.actShowCalibration)

        toolMenu = QMenu("Too&l", self)
        actCreateTerminal = QAction('&Terminal', self, triggered=self.createTerminal)
        actCreateTablePlotter = QAction('Table &Plotter', self, triggered=self.createTablePlotter)
        actCreateNodeEditor = QAction('&Node Editor', self, triggered=self.createNodeEditor)
        actCreateSimpleGraphWindow = QAction('&Simple Graph', self, triggered=self.createSimpleGraphWindow)
        actCreateRawDataGraphWindow = QAction('&Raw Data Graph', self, triggered=self.createRawDataGraphWindow)
        actCreateBetriebsmesstechnikWindow = QAction('&Betriebsmesstechnik', self, triggered=self.createBetriebsmesstechnikWindow)
        actCreateTeleTableViewWindow = QAction('Tele Table &View', self, triggered=self.createTeleTableViewWindow)
        actCreateSynthetischeDatenWindow = QAction('Synthetische &Daten', self, triggered=self.createSynthetischeDatenWindow)
        actCreateTempCalFritoeseWindow = QAction('Temp. Cal. &Fritteuse', self,triggered=self.createTempCalFritoeseWindow)
        actCreateStationaritaetWindow = QAction('Stat&ionaritaet', self,triggered=self.createStationaritaetWindow)
        actCreateProgrammerWindow = QAction('Pr&ogrammer', self, triggered=self.createProgrammerWindow)
        actCreateTestWindow = QAction('T&est', self, triggered=self.createTestWindow)
        toolMenu.addAction(actCreateTerminal)
        toolMenu.addAction(actCreateTablePlotter)
        toolMenu.addAction(actCreateNodeEditor)
        toolMenu.addAction(actCreateSimpleGraphWindow)
        toolMenu.addAction(actCreateRawDataGraphWindow)
        toolMenu.addAction(actCreateBetriebsmesstechnikWindow)
        toolMenu.addAction(actCreateTeleTableViewWindow)
        toolMenu.addAction(actCreateSynthetischeDatenWindow)
        toolMenu.addAction(actCreateTempCalFritoeseWindow)
        toolMenu.addAction(actCreateStationaritaetWindow)
        toolMenu.addAction(actCreateProgrammerWindow)
        toolMenu.addAction(actCreateTestWindow)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(portMenu)
        self.menuBar().addMenu(tableMenu)
        self.menuBar().addMenu(toolMenu)

    def openSerialConnectWindow(self, portName: str):
        self.serialConnectWindow = SerialConnectWindow(portName)
        self.serialConnectWindow.okButton.clicked.connect(lambda: self.connectToSerial(self.serialConnectWindow, None))
        self.serialConnectWindow.show()

    def connectToSerial(self, window: SerialConnectWindow, serialParam: SerialParameters = None):
        if window is not None:
            serialParam = window.getSerialParameter()
            window.close()

        serialThread = SerialThread(serialParam)
        serialThread.signals.madeConnection.connect(lambda obj: self.madeSerialConnectionSignal.emit(obj))
        serialThread.signals.lostConnection.connect(lambda obj: self.lostSerialConnectionSignal.emit(obj))
        serialThread.signals.receivedData.connect(lambda obj, data: self.receiveSerialDataSignal.emit(obj, data))
        serialThread.signals.failedSendData.connect(lambda obj, data: self.failedSendSerialDataSignal.emit(obj, data))
        serialThread.signals.startRecording.connect(lambda obj: self.startedSerialRecordingSignal.emit(obj))
        serialThread.signals.stopRecording.connect(lambda obj: self.stoppedSerialRecordingSignal.emit(obj))

        self.sendSerialWriteSignal.connect(serialThread.writeSerial)
        self.killSerialConnectionSignal.connect(serialThread.kill)
        self.pauseSerialConnectionSignal.connect(serialThread.pause)
        self.resumeSerialConnectionSignal.connect(serialThread.resume)
        self.startSerialRecordSignal.connect(serialThread.startRecordData)
        self.stopSerialRecordSignal.connect(serialThread.stopRecordData)
        self.pauseSerialRecordSignal.connect(serialThread.pauseRecordData)
        self.resumeSerialRecordSignal.connect(serialThread.resumeRecordData)
        self.writeToFileSignal.connect(serialThread.writeDataToFile)

        if QThreadPool.maxThreadCount(QThreadPool.globalInstance()) < QThreadPool.activeThreadCount(QThreadPool.globalInstance()) + 2:
            QThreadPool.setMaxThreadCount(QThreadPool.globalInstance(), QThreadPool.activeThreadCount(QThreadPool.globalInstance()) + 2)
        # QThreadPool.globalInstance().start(serialThread)
        if not QThreadPool.globalInstance().tryStart(serialThread):
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Thread reserve fail")
            dlg.setText("Attempt to reserve a thread to run runnable failed. \n "
                        "Please check if you PC has enough threads to run a new instance.")
            dlg.setStandardButtons(QMessageBox.Ok)
            dlg.setIcon(QMessageBox.Information)
            print("Max thread count: ", QThreadPool.maxThreadCount(QThreadPool.globalInstance()))
            print("Current active thread count: ", QThreadPool.activeThreadCount(QThreadPool.globalInstance()))

    def killSerialConnection(self, portName):
        self.killSerialConnectionSignal.emit(portName)

    def serialWriteData(self, portName: str, data):
        for port in portName.split("|"):
            if port != "":
                self.sendSerialWriteSignal.emit(port, data)

    def startSerialRecord(self, portName, filePath, fileName):
        self.startSerialRecordSignal.emit(portName, filePath, fileName)

    def stopSerialRecord(self, portName):
        self.stopSerialRecordSignal.emit(portName)

    def pauseSerialRecord(self, portName):
        self.pauseSerialRecordSignal.emit(portName)

    def resumeSerialRecord(self, portName):
        self.resumeSerialRecordSignal.emit(portName)

    def writeToFile(self, text, portName, filePath, fileName):
        self.writeToFileSignal.emit(text, portName, filePath, fileName)

    def pauseSerialConnection(self, portName="ALL"):
        self.pauseSerialConnectionSignal.emit(portName)

    def resumeSerialConnection(self, portName="ALL"):
        self.resumeSerialConnectionSignal.emit(portName)

    def printMadeConnection(self, obj: SerialParameters):
        row = self.tableFindOrAddComRow(obj)
        self.table.item(row, 1).setText(obj.port)
        self.table.item(row, 2).setText(str(obj.baudrate))
        self.table.item(row, 3).setText(obj.readTextIndex)
        self.table.cellWidget(row, 4).setText("Connected")
        self.table.cellWidget(row, 4).setStyleSheet("background-color : green")
        self.table.cellWidget(row, 4).setProperty("serialParameter", obj)

        self.connectedPorts.append(obj)
        print("Made connection with: " + obj.port)

    def printLostConnection(self, obj):
        for port in self.connectedPorts:
            if port.port == obj.port:
                self.connectedPorts.remove(port)
        row = self.tableFindComRow(obj.port)
        if row is not None:
            self.table.cellWidget(row, 4).setText("Disconnected")
            self.table.cellWidget(row, 4).setStyleSheet("background-color : red")
            self.table.cellWidget(row, 5).setText("Start Recording")
            self.table.cellWidget(row, 5).setStyleSheet("background-color : gray")
        print("Lost connection with: " + obj.port)

        if obj.autoReconnect == True:
            self.autoReconnectConnectionTimer = QTimer()
            self.autoReconnectConnectionTimer.timeout.connect(lambda: self.autoReconnectConnection(obj, self.autoReconnectConnectionTimer))
            self.autoReconnectConnectionTimer.start(500)

    def autoReconnectConnection(self, serialParameter: SerialParameters, timer: QTimer):
        for port in self.connectedPorts:
            if port.port == serialParameter.port:
                self.recordButtonPressed(serialParameter)
                timer.stop()
                return None
        self.connectToSerial(None, serialParameter)


    def printReceivedData(self, obj, data, dataType = None):
        if dataType is not None:
            self.receiveCalibratedSerialDataSignal.emit(obj, data, dataType)
            return

        self.receiveCalibratedSerialDataSignal.emit(obj, data, {"dataType": "RAW-Values"})

        calibratedData = self.calibrateRawData(obj.port, data)
        if calibratedData is not None:
            self.receiveCalibratedSerialDataSignal.emit(obj, calibratedData, {"dataType": "CALIBRATED-Values"})



    def printFailedSendData(self, obj, data):
        pass

    def printStartRecording(self, obj):
        row = self.tableFindComRow(obj.port)
        if row is not None:
            self.table.cellWidget(row, 5).setText("Stop Recording")
            self.table.cellWidget(row, 5).setStyleSheet("background-color : green")

    def printStopRecording(self, obj):
        row = self.tableFindComRow(obj.port)
        if row is not None:
            self.table.cellWidget(row, 5).setText("Start Recording")
            self.table.cellWidget(row, 5).setStyleSheet("background-color : gray")

    def closeEvent(self, event):
        self.fileSave(str(Path(os.getcwd() + "/last_save.json")))
        for window in self.windows:
            # Bisschen strange: eigentlich wollte ich window.close() benutzen, aber wenn mehr als ein Fenster offen ist, schließt das letzte Fenster nicht mehr --> überprüfen
            window.onClosing()
            window.deleteLater()
        self.killSerialConnection("ALL")

    def deleteWindowFromList(self, window):
        self.windows.remove(window)

    def tableShowColumn(self, column: int, checked: bool):
        if checked:
            self.table.showColumn(column)
        else:
            self.table.hideColumn(column)

    def tableFindOrAddComRow(self, obj: SerialParameters):
        if self.tableFindComRow(obj.port) is not None:
            return self.tableFindComRow(obj.port)
        return self.tableAddRow(obj)

    def tableAddRow(self, obj: SerialParameters):
        self.table.insertRow(self.table.rowCount())

        deleteConnectionButton = QPushButton()
        deleteConnectionButton.setIcon(QIcon(resource_path(str(Path("res/Icon/close.ico")))))
        deleteConnectionButton.clicked.connect(lambda: self.deleteConnectionButtonPressed(obj.port))
        self.table.setCellWidget(self.table.rowCount() - 1, 0, deleteConnectionButton)

        self.table.setItem(self.table.rowCount() - 1, 1, QTableWidgetItem(obj.port))
        self.table.item(self.table.rowCount() - 1, 1).setTextAlignment(Qt.AlignCenter)
        self.table.item(self.table.rowCount() - 1, 1).setFlags(Qt.ItemIsEnabled)
        self.table.setItem(self.table.rowCount() - 1, 2, QTableWidgetItem(str(obj.baudrate)))
        self.table.item(self.table.rowCount() - 1, 2).setTextAlignment(Qt.AlignCenter)
        self.table.item(self.table.rowCount() - 1, 2).setFlags(Qt.ItemIsEnabled)
        self.table.setItem(self.table.rowCount() - 1, 3, QTableWidgetItem(obj.readTextIndex))
        self.table.item(self.table.rowCount() - 1, 3).setTextAlignment(Qt.AlignCenter)
        self.table.item(self.table.rowCount() - 1, 3).setFlags(Qt.ItemIsEnabled)

        connectedButton = QPushButton("Disconnected")
        connectedButton.setStyleSheet("background-color : red")
        connectedButton.setProperty("serialParameter", obj)
        connectedButton.clicked.connect(lambda: self.connectButtonPressed(connectedButton, obj))
        self.table.setCellWidget(self.table.rowCount() - 1, 4, connectedButton)

        recordButton = QPushButton("Start Recording")
        recordButton.setStyleSheet("background-color : gray")
        recordButton.setProperty("path", os.getcwd())
        recordButton.setToolTip(recordButton.property("path"))
        recordButton.clicked.connect(lambda: self.recordButtonPressed(obj))
        self.table.setCellWidget(self.table.rowCount() - 1, 5, recordButton)

        openFilePathDialogButton = QPushButton()
        openFilePathDialogButton.setIcon(QIcon(resource_path("res/Icon/folder.ico")))
        openFilePathDialogButton.setToolTip(recordButton.property("path"))
        openFilePathDialogButton.setIconSize(QSize(25, 25))
        openFilePathDialogButton.clicked.connect(lambda: self.recordPathButtonPressed(obj.port))
        self.table.setCellWidget(self.table.rowCount() - 1, 6, openFilePathDialogButton)

        recordNameButton = QLineEdit("DATE_TIME")
        recordNameButton.setToolTip(
            "DATE: replaced to jjjj-mm-dd | TIME: replaced to hh-mm-ss | PORT: replaced to port | BAUD: replaced to baud")
        self.table.setCellWidget(self.table.rowCount() - 1, 7, recordNameButton)

        calibrationPathDialogButton = QPushButton()
        calibrationPathDialogButton.setIcon(QIcon(resource_path("res/Icon/folder.ico")))
        calibrationPathDialogButton.setProperty("path", "")
        calibrationPathDialogButton.setToolTip(calibrationPathDialogButton.property("path"))
        calibrationPathDialogButton.setIconSize(QSize(25, 25))
        calibrationPathDialogButton.clicked.connect(lambda: self.calibrationPathButtonPressed(obj.port))
        self.table.setCellWidget(self.table.rowCount() - 1, 8, calibrationPathDialogButton)

        return self.table.rowCount() - 1

    def measuringPointListTableAddRow(self, filePath):
        self.measuringPointListTable.insertRow(self.measuringPointListTable.rowCount())

        measuringPointListLabel = QPushButton(os.path.basename(filePath))
        measuringPointListLabel.clicked.connect(lambda: self.showMeasuringPointListTable(filePath))
        measuringPointListLabel.setProperty("path", filePath)
        measuringPointListLabel.setToolTip(measuringPointListLabel.property("path"))
        self.measuringPointListTable.setCellWidget(self.measuringPointListTable.rowCount() - 1, 0, measuringPointListLabel)

        self.measuringPointListTable.show()

        return self.measuringPointListTable.rowCount() - 1

    def tableFindComRow(self, comName: str):
        for countY in range(0, self.table.rowCount()):
            if self.table.item(countY, 1).text() == comName:
                return countY
        return None

    def connectButtonPressed(self, button: QPushButton, obj: SerialParameters):
        if button.text() == "Connected":
            self.killSerialConnection(obj.port)
        else:
            self.connectToSerial(None, obj)


    def recordButtonPressed(self, obj):
        row = self.tableFindComRow(obj.port)
        if row is not None:
            if self.table.cellWidget(row, 5).text() == "Start Recording":
                filename = self.table.cellWidget(row, 7).text()
                filename = filename.replace("PORT", obj.port)
                filename = filename.replace("BAUD", str(obj.baudrate))
                filename = filename.replace("DATE", datetime.now().strftime("%Y-%m-%d"))
                filename = filename.replace("TIME", datetime.now().strftime("%H-%M-%S"))
                filename += ".txt"
                self.startSerialRecord(obj.port, self.table.cellWidget(row, 5).property("path"), filename)
            elif self.table.cellWidget(row, 5).text() == "Stop Recording":
                self.stopSerialRecord(obj.port)

    def recordPathButtonPressed(self, port):
        row = self.tableFindComRow(port)
        if row is not None:
            path = QFileDialog.getExistingDirectory(None, "Select Folder", "",
                                                    QFileDialog.DontUseNativeDialog | QFileDialog.ShowDirsOnly)
            self.checkForValidRecordPath(port, path)

    def checkForValidRecordPath(self, port, path):
        if path and os.path.isdir(path):
            row = self.tableFindComRow(port)
            button = self.table.cellWidget(row, 5)
            button.setProperty("path", path)
            self.table.cellWidget(row, 6).setToolTip(path)
            button.setToolTip(path)

    def deleteConnectionButtonPressed(self, port):
        if self.returnMsgBoxAnswerYesNo("Close Connection!", "Willst du diese Verbindung löschen?") == QMessageBox.Yes:
            self.killSerialConnection(port)
            self.table.removeRow(self.tableFindComRow(port))

    def calibrationPathButtonPressed(self, port):
        row = self.tableFindComRow(port)
        if row is not None:
            filePaths, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file', "", "", "",
                                                             QFileDialog.DontUseNativeDialog)
            self.checkForValidCalibrationFile(port, filePaths)

    def checkForValidCalibrationFile(self, port, filePaths):
        loadCalibrationFailed = False
        buttonProperty = []
        row = self.tableFindComRow(port)
        button = self.table.cellWidget(row, 8)

        if port in self.calibrationFiles:
            del self.calibrationFiles[port]

        for filePath in filePaths:
            if filePath != '' and os.path.isfile(filePath):
                if self.loadCalibrationFile(filePath, port) is not False:
                    buttonProperty.append(filePath)
                else:
                    loadCalibrationFailed = True
            else:
                loadCalibrationFailed = True
        if loadCalibrationFailed:
            button.setIcon(QIcon(resource_path("res/Icon/folder_with_red_exclamationmark.ico")))
        else:
            button.setIcon(QIcon(resource_path("res/Icon/folder_with_green_checkmark.ico")))
        if buttonProperty != []:
            button.setProperty("path", buttonProperty)
            button.setToolTip("\n".join(buttonProperty))

    def loadCalibrationFile(self, filePath: str, port):
        headings = []
        calData = []

        with open(filePath, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';')
            line_count = 0
            for row in spamreader:
                if line_count == 0:
                    headings = row
                else:
                    if len(row) == 8:
                        try:
                            calData.append(
                                [row[0],  # UUID
                                 row[1],  # Name
                                 json.loads(row[2]),  # KalKoeff
                                 row[3],  # KalFunkTyp
                                 json.loads(row[4]),  # DifferenzKanal
                                 row[5],  # Messwert
                                 strToFloatElseNone(row[6]),  # FitFehler
                                 json.loads(row[7])]  # Kommentar
                            )
                        except Exception as e:
                            print(str(e))
                            return False
                    else:
                        print("Column count of calibration file not 8")
                        return False
                line_count += 1

        if port in self.calibrationFiles:
            if not str(len(calData)) in self.calibrationFiles[port]:
                self.calibrationFiles[port][str(len(calData))] = {"PATH": filePath,
                                                                  "NAME": os.path.basename(filePath),
                                                                  "HEADINGS": headings,
                                                                  "CALIBRATIONDATA": calData}
            else:
                return False
        else:
            self.calibrationFiles[port] = {str(len(calData)): {"PATH": filePath,
                                                               "NAME": os.path.basename(filePath),
                                                               "HEADINGS": headings,
                                                               "CALIBRATIONDATA": calData}}

        return filePath

    def loadMeasuringPointListFile(self, filePath: str):
        headings = []
        dataInfo = []
        dataInfo_t = {}

        with open(filePath, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';')
            line_count = 0
            for row in spamreader:
                if line_count == 0:
                    headings = row
                else:
                    try:
                        dataInfo.append(row)
                    except Exception as e:
                        print(str(e))
                        return False
                line_count += 1


            for i in range(len(dataInfo[0])):
                tmp = []
                for v in dataInfo:
                    tmp.append(v[i])
                dataInfo_t[headings[i]] = tmp
        self.measuringPointListFiles.append({"PATH": filePath,
                                            "NAME": os.path.basename(filePath),
                                            "HEADINGS": headings,
                                            "DATA": dataInfo_t})

    def showMeasuringPointListTable(self, path: str):
        self.mplw = MeasuringPointListWindow(path, self.measuringPointListFiles)
        self.mplw.show()

    def showGlobalVars(self):
        self.globalVarsLabel = ScrollableLabelWindow(json.dumps(self.globalVars, indent=2))
        self.globalVarsLabel.show()

    def calibrateRawData(self, port: str, data):
        if port in self.calibrationFiles:
            if str(len(data) - 1) in self.calibrationFiles[port]:
                calData = self.calibrationFiles[port][str(len(data) - 1)]["CALIBRATIONDATA"]
                calibratedData = applyCalibrationFunctions(calData, data)
                return calibratedData
        return None

    def returnMsgBoxAnswerYesNo(self, title: str = "Message", text: str = ""):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        return dlg.exec()

    def showInfoBox(self, title: str = "Message", text: str = ""):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Information)
        return dlg.exec()

    def connectWindowToSignals(self, window: AbstractWindow):
        self.madeSerialConnectionSignal.connect(window.madeSerialConnection)
        self.lostSerialConnectionSignal.connect(window.lostSerialConnection)
        self.receiveCalibratedSerialDataSignal.connect(window.receiveCalibratedSerialData)
        self.failedSendSerialDataSignal.connect(window.failedSendSerialData)
        self.startedSerialRecordingSignal.connect(window.startedSerialRecording)
        self.stoppedSerialRecordingSignal.connect(window.stopSerialRecording)
        self.globalVarsChangedSignal.connect(window.globalVarsChanged)

        window.sendSerialWriteSignal.connect(self.serialWriteData)
        window.killSerialConnectionSignal.connect(self.killSerialConnection)
        window.startSerialRecordSignal.connect(self.startSerialRecord)
        window.stopSerialRecordSignal.connect(self.stopSerialRecord)
        window.writeToFileSignal.connect(self.writeToFile)

    def createTerminal(self):
        window = WindowTerminal(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window

    def createTablePlotter(self):
        window = WindowTablePlotter(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window

    def createNodeEditor(self):
        window = WindowNodeEditor(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window

    def createSimpleGraphWindow(self):
        window = WindowSimpleGraph(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window

    def createRawDataGraphWindow(self):
        window = WindowRawDataGraph(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window

    def createBetriebsmesstechnikWindow(self):
        window = WindowBetriebsmesstechnik(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window

    def createTeleTableViewWindow(self):
        window = WindowTeleTableView(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window

    def createSynthetischeDatenWindow(self):
        window = WindowSynthetischeDaten(self)
        self.windows.append(window)
        return window

    def createTempCalFritoeseWindow(self):
        window = WindowTempCalFritoese(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window
    
    def createStationaritaetWindow(self):
        window = WindowStationaritaet(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window

    def createProgrammerWindow(self):
        window = WindowProgrammer(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window

    def createTestWindow(self):
        window = WindowTest(self)
        self.windows.append(window)
        self.connectWindowToSignals(window)
        return window

    def onFileSaveAs(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'Save current layout to file', None, "*.json", "",
                                                    QFileDialog.DontUseNativeDialog)
        if fname == '': return False
        if fname.split(".")[-1] != "json": fname += ".json"
        self.fileSave(fname)
        self.statusBar().showMessage("Successfully saved as %s" % fname, 5000)

        self.setWindowTitle("Com Utility Manager: " + str(os.path.basename(fname).split(".")[0]))
        return True

    def onFileOpen(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file', "", "*.json", "",
                                                    QFileDialog.DontUseNativeDialog)
        if fname != '' and os.path.isfile(fname):
            self.loadFromFile(fname)
            self.setWindowTitle("Com Utility Manager: " + str(os.path.basename(fname)))

    def onMeasurementListOpen(self):
        filePaths, filter = QFileDialog.getOpenFileNames(self, 'Open measurement list from file', "", "", "",
                                                         QFileDialog.DontUseNativeDialog)
        if filePaths == []:
            return
        while self.measuringPointListTable.rowCount() > 0:
            self.measuringPointListTable.removeRow(0)
        self.measuringPointListFiles = []

        for filePath in filePaths:
            if filePath != '' and os.path.isfile(filePath):
                self.loadMeasuringPointListFile(filePath)
                self.measuringPointListTableAddRow(filePath)
            else:
                print("File not existing!")

    def onGlobalVarsOpen(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file', "", "*.json", "",
                                                    QFileDialog.DontUseNativeDialog)
        if fname != '' and os.path.isfile(fname):
            with open(fname, "r") as file:
                raw_data = file.read()
                try:
                    self.globalVars = json.loads(raw_data)
                    if type(self.globalVars) != dict:
                        self.globalVars = {}
                        self.showInfoBox("Wrong format!", "JSON file should only contain exactly one dictionary.")
                    else:
                        self.globalVarsChangedSignal.emit("", "ALL")
                except Exception as e:
                    self.showInfoBox("Loading failed!", repr(e))

    def setGlobalVars(self, dictionary: dict, senderID: str = "", keyChanged: str = "ALL"):
        self.globalVars = dictionary
        self.globalVarsChangedSignal.emit(senderID, keyChanged)

    def setGlobalVarsEntry(self, key: str, value, senderID: str = "", keyChanged: str = ""):
        self.globalVars[key] = value
        self.globalVarsChangedSignal.emit(senderID, keyChanged)

    def fileSave(self, filename: str = None):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
            print("saving to", filename, "was successfull.")
        QApplication.restoreOverrideCursor()
        return True

    def loadFromFile(self, filename: str):
        with open(filename, "r") as file:
            raw_data = file.read()
            try:
                if sys.version_info >= (3, 9):
                    data = json.loads(raw_data)
                else:
                    data = json.loads(raw_data, encoding='utf-8')
                self.deserialize(data)
            except json.JSONDecodeError:
                raise TypeError("%s is not a valid JSON file" % os.path.basename(filename))
            except Exception as e:
                print(e)

    def serialize(self) -> OrderedDict:
        ports = []
        measuringPointListFiles = []
        windows = []

        for countY in range(0, self.table.rowCount()):
            dummyDict = self.table.cellWidget(countY, 4).property("serialParameter").serialize()
            savePath = self.table.cellWidget(countY, 5).property("path")
            saveName = self.table.cellWidget(countY, 7).text()
            calibrationPath = self.table.cellWidget(countY, 8).property("path")
            ports.append({"serialParameter": dummyDict, "savePath": savePath, "saveName": saveName,
                          "calibrationPath": calibrationPath})

        for countY in range(0, self.measuringPointListTable.rowCount()):
            savePath = self.measuringPointListTable.cellWidget(countY, 0).property("path")
            measuringPointListFiles.append({"savePath": savePath})

        for window in self.windows:
            windows.append(window.serialize())

        tableColumnShown = []
        for countX in range(0, self.table.columnCount()):
            tableColumnShown.append(self.table.isColumnHidden(countX))

        return OrderedDict([
            ("_windowType", self._windowType),
            ('_windowSize', [self.size().width(), self.size().height()]),
            ('_windowPosition', [self.pos().x(), self.pos().y()]),
            ('_windowMaximized', self.isMaximized()),
            ('_tableColumnsHidden', tableColumnShown),
            ('ports', ports),
            ('measuringPointListFiles', measuringPointListFiles),
            ('windows', windows),
            ('globalVars', self.globalVars)
        ])

    def deserialize(self, data: dict) -> bool:
        if data['_windowType'] != "Hub":
            print("Not the right save file! Window type: " + str(data['_windowType']))
            return

        for window in self.windows:
            window.close()

        while self.measuringPointListTable.rowCount() > 0:
            self.measuringPointListTable.removeRow(0)
        self.measuringPointListFiles = []

        self.resize(data['_windowSize'][0], data['_windowSize'][1])

        # Check if Window is outside of screen:    Auskommentiert, weil unnütz für die meisten Fälle
        #if (QApplication.primaryScreen().size().width() < data['_windowPosition'][0] + data['_windowSize'][0] or
        #    data['_windowPosition'][0] < 0 or QApplication.primaryScreen().size().height() < data['_windowPosition'][
        #        1] + data['_windowSize'][1] or data['_windowPosition'][1] < 0) and self.returnMsgBoxAnswerYesNo(
        #        "Out Of Screen",
        #        "Window \"Hub\" is out of screen!\nDo you want to move it inside the screen?") == QMessageBox.Yes:
        #    self.move(max(0, min(data['_windowPosition'][0],
        #                         QApplication.primaryScreen().size().width() - data['_windowSize'][0])), max(0, min(
        #        data['_windowPosition'][1], QApplication.primaryScreen().size().height() - data['_windowSize'][1])))
        #else:
        #    self.move(data['_windowPosition'][0], data['_windowPosition'][1])
        self.move(data['_windowPosition'][0], data['_windowPosition'][1])

        if data['_windowMaximized'] == True:
            self.showMaximized()

        self.actShowDelete.setChecked(not data['_tableColumnsHidden'][0])
        self.actShowCom.setChecked(not data['_tableColumnsHidden'][1])
        self.actShowBaud.setChecked(not data['_tableColumnsHidden'][2])
        self.actShowType.setChecked(not data['_tableColumnsHidden'][3])
        self.actShowStatus.setChecked(not data['_tableColumnsHidden'][4])
        self.actShowRecord.setChecked(not data['_tableColumnsHidden'][5])
        self.actShowPath.setChecked(not data['_tableColumnsHidden'][6])
        self.actShowRecordName.setChecked(not data['_tableColumnsHidden'][7])
        self.actShowCalibration.setChecked(not data['_tableColumnsHidden'][8])

        for countX in range(0, self.table.columnCount()):
            self.table.hideColumn(countX) if data['_tableColumnsHidden'][countX] else self.table.showColumn(countX)

        for port_data in data['ports']:
            serialParameter = SerialParameters()
            serialParameter.deserialize(port_data["serialParameter"])
            if any(param.port == serialParameter.port for param in self.connectedPorts):
                QMessageBox.about(self, "Port occupied",
                                  "Der Port \"" + str(serialParameter.port) + "\" ist schon connected!")
                continue

            self.tableFindOrAddComRow(serialParameter)
            self.checkForValidRecordPath(serialParameter.port, port_data["savePath"])
            row = self.tableFindComRow(serialParameter.port)
            self.table.cellWidget(row, 7).setText(port_data["saveName"])
            if port_data["calibrationPath"] != "":
                self.checkForValidCalibrationFile(serialParameter.port, port_data["calibrationPath"])
            self.connectToSerial(None, serialParameter)

        for measuringPointListFileData in data['measuringPointListFiles']:
            filePath = measuringPointListFileData["savePath"]
            if filePath != '' and os.path.isfile(filePath):
                self.loadMeasuringPointListFile(filePath)
                self.measuringPointListTableAddRow(filePath)
            else:
                print("File not existing!")


        for window_data in data['windows']:
            if window_data["_windowType"] == "Terminal":
                self.createTerminal().deserialize(window_data)
            if window_data["_windowType"] == "TablePlotter":
                self.createTablePlotter().deserialize(window_data)
            if window_data["_windowType"] == "NodeEditor":
                self.createNodeEditor().deserialize(window_data)
            if window_data["_windowType"] == "SimpleGraph":
                self.createSimpleGraphWindow().deserialize(window_data)
            if window_data["_windowType"] == "RawDataGraph":
                self.createRawDataGraphWindow().deserialize(window_data)
            if window_data["_windowType"] == "Betriebsmesstechnik":
                self.createBetriebsmesstechnikWindow().deserialize(window_data)
            if window_data["_windowType"] == "TeleTableView":
                self.createTeleTableViewWindow().deserialize(window_data)
            if window_data["_windowType"] == "SynthetischeDaten":
                self.createSynthetischeDatenWindow().deserialize(window_data)
            if window_data["_windowType"] == "TempCalFritteuse":
                self.createTempCalFritoeseWindow().deserialize(window_data)
            if window_data["_windowType"] == "Stationaritaet":
                self.createStationaritaetWindow().deserialize(window_data)
            if window_data["_windowType"] == "Programmer":
                self.createProgrammerWindow().deserialize(window_data)
            if window_data["_windowType"] == "Test":
                self.createTestWindow().deserialize(window_data)

        self.globalVars = data['globalVars']

