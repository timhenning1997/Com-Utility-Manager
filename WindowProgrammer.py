import binascii
import os
import re
import sys
import time
import csv
import traceback

import libscrc
from PyQt5.QtCore import QPoint, Qt, QRunnable, pyqtSlot, QThreadPool, QProcess, QRegExp, pyqtSignal, QObject
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, \
    QGridLayout, QTextEdit, QSplitter, QAction, QFileDialog, QApplication, QMessageBox
from PyQt5.QtGui import QPixmap, QFont, QTextDocument, QSyntaxHighlighter, QColor, QTextCharFormat, QCloseEvent
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from time import sleep
from datetime import datetime


def tempFormat(color, style=''):
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)
    return _format


class PythonHighlighter (QSyntaxHighlighter):
    STYLESENABLED = {
        'keyword': tempFormat('#7986CB'),
        'operator': tempFormat('#9575CD'),
        'brace': tempFormat('#A1887F'),
        'defclass': tempFormat('#00897B', 'bold'),
        'string': tempFormat('#90A4AE', 'italic'),
        'string2': tempFormat('#26A69A'),
        'comment': tempFormat('#546E7A', 'italic'),
        'self': tempFormat('#7E57C2', 'italic'),
        'numbers': tempFormat('#6897bb'),
    }

    STYLESDISABLED = {
        'keyword': tempFormat('#999999'),
        'operator': tempFormat('#999999'),
        'brace': tempFormat('#999999'),
        'defclass': tempFormat('#999999', 'bold'),
        'string': tempFormat('#999999', 'italic'),
        'string2': tempFormat('#999999'),
        'comment': tempFormat('#999999', 'italic'),
        'self': tempFormat('#999999', 'italic'),
        'numbers': tempFormat('#999999'),
    }

    keywords = ['and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False']

    operators = ['=', '==', '!=', '<', '<=', '>', '>=', '\+', '-', '\*', '/', '//', '\%', '\*\*', '\+=', '-=', '\*=', '/=', '\%=', '\^', '\|', '\&', '\~', '>>', '<<']
    braces = ['\{', '\}', '\(', '\)', '\[', '\]']

    def __init__(self, parent: QTextDocument) -> None:
        super().__init__(parent)
        self.tri_single = (QRegExp("'''"), 1, self.STYLESENABLED['string2'])
        self.tri_double = (QRegExp('"""'), 2, self.STYLESENABLED['string2'])

        rules = []
        rules += [(r'\b%s\b' % w, 0, self.STYLESENABLED['keyword'])
            for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, self.STYLESENABLED['operator'])
            for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, self.STYLESENABLED['brace'])
            for b in PythonHighlighter.braces]
        rules += [
            (r'\bself\b', 0, self.STYLESENABLED['self']),
            (r'\bdef\b\s*(\w+)', 1, self.STYLESENABLED['defclass']),
            (r'\bclass\b\s*(\w+)', 1, self.STYLESENABLED['defclass']),
            (r'\b[+-]?[0-9]+[lL]?\b', 0, self.STYLESENABLED['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, self.STYLESENABLED['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, self.STYLESENABLED['numbers']),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.STYLESENABLED['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.STYLESENABLED['string']),
            (r'#[^\n]*', 0, self.STYLESENABLED['comment'])]

        self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        self.tripleQuoutesWithinStrings = []
        for expression, nth, tempFormat in self.rules:
            index = expression.indexIn(text, 0)
            if index >= 0:
                if expression.pattern() in [r'"[^"\\]*(\\.[^"\\]*)*"', r"'[^'\\]*(\\.[^'\\]*)*'"]:
                    innerIndex = self.tri_single[0].indexIn(text, index + 1)
                    if innerIndex == -1:
                        innerIndex = self.tri_double[0].indexIn(text, index + 1)

                    if innerIndex != -1:
                        tripleQuoteIndexes = range(innerIndex, innerIndex + 3)
                        self.tripleQuoutesWithinStrings.extend(tripleQuoteIndexes)

            while index >= 0:
                if index in self.tripleQuoutesWithinStrings:
                    index += 1
                    expression.indexIn(text, index)
                    continue

                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, tempFormat)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        else:
            start = delimiter.indexIn(text)
            if start in self.tripleQuoutesWithinStrings:
                return False
            add = delimiter.matchedLength()

        while start >= 0:
            end = delimiter.indexIn(text, start + add)
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            self.setFormat(start, length, style)
            start = delimiter.indexIn(text, start + length)

        if self.currentBlockState() == in_state:
            return True
        else:
            return False

    def setEnableHighlighting(self, b: bool):
        if b:
            styles = self.STYLESENABLED
        else:
            styles = self.STYLESDISABLED
        self.tri_single = (QRegExp("'''"), 1, styles['string2'])
        self.tri_double = (QRegExp('"""'), 2, styles['string2'])

        rules = []
        rules += [(r'\b%s\b' % w, 0, styles['keyword'])
                  for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, styles['operator'])
                  for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, styles['brace'])
                  for b in PythonHighlighter.braces]
        rules += [
            (r'\bself\b', 0, styles['self']),
            (r'\bdef\b\s*(\w+)', 1, styles['defclass']),
            (r'\bclass\b\s*(\w+)', 1, styles['defclass']),
            (r'\b[+-]?[0-9]+[lL]?\b', 0, styles['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, styles['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, styles['numbers']),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, styles['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, styles['string']),
            (r'#[^\n]*', 0, styles['comment'])]

        self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]


class SerialSignals(QObject):
    sendDataSignal = pyqtSignal(object, object)
    forwardDataSignal = pyqtSignal(object, object, object)
    sendOutputSignal = pyqtSignal(object)
    sendErrorSignal = pyqtSignal(object)
    stoppedRunningSignal = pyqtSignal()


class Worker(QRunnable):
    def __init__(self):
        super().__init__()

        self.is_killed = False
        self.running = False
        self.looping = False
        self.stopping = False

        self.signals = SerialSignals()
        self.program = ""

        self.globalDevice = None
        self.globalPort = None
        self.globalTimeout = None
        self.globalRetry = 0
        self.globalDelay = 0.1

        self.lastData = None
        self.lastSerialParameters = None
        self.lastDataInfo = None
        self.lastPort = None

        self.lastDataRead = False
    @pyqtSlot()
    def run(self):
        while not self.is_killed:
            if self.running == True:
                try:
                    self.initVars()
                    exec(self.program)
                except Exception as inst:
                    self.signals.sendErrorSignal.emit(inst)
                    self.running = False
                    self.signals.stoppedRunningSignal.emit()

                if self.looping == True:
                    if self.stopping == True:
                        self.running = False
                        self.signals.stoppedRunningSignal.emit()
                    self.stopping = False
                else:
                    self.running = False
                    self.signals.stoppedRunningSignal.emit()
                sleep(0.01)
            else:
                sleep(0.1)

    def initVars(self):
        self.globalDevice = ""
        self.globalPort = None
        self.globalTimeout = None
        self.globalRetry = 0

    def query(self, message=None, device: str = None, command: str = None, value=None, unit=None, port=None, timeout: float = None, delay=None, retry: int = None):
        self.lastData = None

        # apply global variables if necessary
        device = self.globalDevice if device is None else device
        port = self.globalPort if port is None else port
        timeout = self.globalTimeout if timeout is None else timeout
        delay = self.globalDelay if delay is None else delay
        retry = self.globalRetry if retry is None else retry

        if device.lower() == "fritteuse":
            if command.lower() in ["t", "temp", "temperature"]:
                message = "{M01****\r\n"
            elif command.lower() in ["setpointtemp", "setpointtemperature", "set", "setpoint", "soll", "sollwert", "setzesollwert"]:
                message = "{M71" + format(int(value * 100), 'x').upper().zfill(4) + "\r\n" if type(value) in [int, float] else message
            elif command.lower() in ["tempcontrol", "temperaturecontrol", "settempcontrol", "settemperaturecontrol", "settempcon", "control"]:
                message = "{M14000" + str(int(value)) + "\r\n" if type(value) in [bool] else message
        elif device.lower() in ["keithley2010", "keithley"]:
            if command.lower() in ["meas", "measure", "messen", "ask", "askfor", "query", "request"]:
                if type(value)==list and len(value)==3:
                    message = [":SENS:FUNC \"" + str(value[1]) + "\"\r\n", ":SENS:FRES:RANG " + str(value[2]) + "\r\n", "ROUTE:CLOSE (@" + str(value[0]) + ")\r\n", ":READ?\r\n"]
        elif device.lower() in ["fluke6270a", "fluke", "fluke6270", "druckkalibrator"]:
            if command.lower() in ["get_unit", "getunit", "unit", "einheit"]:
                message = "UNIT:PRES?\r\n"
            elif command.lower() in ["readycheck", "ready_check", "is_ready", "isready", "bereit", "ready"]:
                message = "STAT:OPER:COND?\r\n"
            if command.lower() in ["get_pressure", "pressure", "istwert", "druck"]:
                message = "MEAS:PRES?\r\n"
            if command.lower() in ["get_uncertainty", "uncertainty", "unsicherheit", "sigma", "sigp", "sigmap"]:
                message = "MEAS:PRES:UNC?\r\n"


        if port is not None:
            if type(port) == str:
                port = [port]
        else:
            port = ["COM-ALL"]

        if message is not None:
            if type(message) == str:
                self.sendData(message, port)
            elif type(message) == list:
                for index in range(0, len(message)):
                    self.sendData(message[index], port)
                    if index < len(message)-1:
                        sleep(delay)
            else:
                return None

        startTime = time.time()

        # Waiting for answer
        while True:
            # Timeout occurred
            if timeout is not None:
                if time.time() - startTime >= timeout:
                    if retry > 0:
                        return self.query(message, device, command, value, unit, port, timeout, delay, retry-1)
                    else:
                        return None

            if self.lastData is not None and (port == "COM-ALL" or "COM-ALL" in port or self.lastPort in port):
                # No device specified
                if device in [None, ""]:
                    return self.lastData

                # Fritteuse specified
                elif device.lower() == "fritteuse":
                    if re.match(r"\{S[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]", self.lastData.decode()):
                        return int(self.lastData.decode().strip()[4:8], 16)

                # Keithley2010 specified
                elif device.lower() in ["keithley2010", "keithley"]:
                    if re.match(r"[+,-][0-9]*[.][0-9]*E[+,-][0-9]*.*", self.lastData.decode()):
                        return float(re.findall("[+,-][0-9]*[.][0-9]*E[+,-][0-9]*", self.lastData.decode().strip())[0])

                # Fluke6270A specified
                elif device.lower() in ["fluke6270a", "fluke", "fluke6270", "druckkalibrator"]:
                    if message == "STAT:OPER:COND?\r\n":
                        if str(self.lastData.decode().strip()) == "16":
                            return True
                        else:
                            return False
                    else:
                        return self.lastData.decode().strip()

                self.lastData = None
                self.lastPort = None
            sleep(0.05)

    def send(self, message: str = None, device: str = None, command: str = None, value=None, unit=None, port=None, delay=None):
        device = self.globalDevice if device is None else device
        port = self.globalPort if port is None else port
        delay = self.globalDelay if delay is None else delay

        if device.lower() in ["keithley2010", "keithley"]:
            if command.lower() in ["init", "begin"]:
                message = ["*RST\r\n", "*CLS\r\n", "INIT:CONT OFF\r\n", "ABORT\r\n"]
        elif device.lower() in ["fluke6270a", "fluke", "fluke6270", "druckkalibrator"]:
            if command.lower() in ["set_unit", "setunit", "unit", "einheit"]:
                if type(value) == str:
                    message = "UNIT:PRES " + str(value).upper() + "\r\n"
                if type(unit) == str:
                    message = "UNIT:PRES " + str(unit).upper() + "\r\n"
            elif command.lower() in ["set_pressurelevel", "setpoint", "sollwert", "soll"]:
                if type(value) in [int, float]:
                    message = "SOUR:PRES:LEV:IMM:AMPL " + str(value) + "\r\n"
            elif command.lower() in ["controllingmode", "control", "start_controll", "regeln", "start_regeln"]:
                message = ["SENS:PRES:MOD AUTO\r\n", "OUTP:PRES:MODE CONT\r\n"]
            elif command.lower() in ["measuremode", "measure", "meas", "messen"]:
                message = "OUTP:PRES:MODE MEAS\r\n"
            elif command.lower() in ["ventmode", "vent", "entlüften", "entlueften", "venting"]:
                message = "OUTP:PRES:MODE VENT\r\n"
            elif command.lower() in ["setinstrpresmode", "pressure_mode", "pressuremode", "setinstrumentpressuremode", "set_instrument_pressure_mode"]:
                message = "SENS:PRES:MODE " + str(value).upper() + "\r\n"



        if port is not None:
            if type(port) == str:
                port = [port]
        else:
            port = ["COM-ALL"]

        if message is not None:
            if type(message) == str:
                self.sendData(message, port)
            elif type(message) == list:
                for index in range(0, len(message)):
                    self.sendData(message[index], port)
                    if index < len(message) - 1:
                        sleep(delay)
            return True
        else:
            return False


    def queryData(self, port=None, dataType=None):
        while True:
            #while self.lastData is None or self.lastDataRead == False:
            #    sleep(0.01)
            if self.lastData is not None and self.lastDataRead == False:
                if port in [self.lastPort, None]:
                    if dataType in [self.lastDataInfo["dataType"], None]:
                        self.lastDataRead = True
                        return self.lastData



    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        self.lastPort = serialParameters.port
        self.lastSerialParameters = serialParameters
        self.lastDataInfo = dataInfo
        self.lastData = data
        self.lastDataRead = False
        self.getData(self, serialParameters, data, dataInfo)

    def getData(self, object_body, serialParameters: SerialParameters, data, dataInfo):
        pass

    def sendData(self, data: str, ports=None):
        if type(ports) == str:
            ports = [ports]
        self.signals.sendDataSignal.emit(data.encode('utf-8'), ports)

    def sendRawData(self, data: str, ports=None):
        if type(ports) == str:
            ports = [ports]
        self.signals.sendDataSignal.emit(data, ports)

    def sendRawWUCommand(self, data: str, ports=None, checksum_ccitt: bool = True, pretext: str = "0F35"):
        if type(ports) == str:
            ports = [ports]
        if checksum_ccitt:
            try:
                checkSum = str(hex(libscrc.ccitt_false(binascii.unhexlify(str(data))))[2:6].rjust(4, '0'))
                _data = pretext + str(data) + str(checkSum)
                _data = binascii.unhexlify(str(_data))
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Send Commandbyte Error")
                msg.setText("There is an error with sending the command bytes")
                msg.exec_()
                return
        else:
            try:
                checkSum = str(hex(libscrc.modbus(binascii.unhexlify(str(data))))[2:6].rjust(4, '0'))
                _data = pretext + str(data) + str(checkSum)
                _data = binascii.unhexlify(str(_data))
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Send Commandbyte Error")
                msg.setText("There is an error with sending the command bytes")
                msg.exec_()
                return

        self.signals.sendDataSignal.emit(_data, ports)

    def sendOutput(self, text):
        self.signals.sendOutputSignal.emit(text)

    def clearOutput(self):
        self.signals.sendOutputSignal.emit("CLEAR_OUTPUT_SIGNAL")

    def forwardData(self, data, serialParameters: SerialParameters = None, dataInfo=None, port: str = None):
        if serialParameters is None:
            if port is None:
                serialParameters = SerialParameters("COM69")
            else:
                serialParameters = SerialParameters(port)

        if type(data) is not str:
            data = str(data)
        data.encode('utf-8')

        self.signals.forwardDataSignal.emit(serialParameters, data, dataInfo)

    def kill(self):
        self.is_killed = True

    def runButtonPressed(self, text):
        self.program = text
        self.running = True

    def loopButtonPressed(self, b: bool):
        self.looping = b

    def stopButtonPressed(self):
        self.stopping = True


class WindowProgrammer(AbstractWindow):
    receiveCalibratedSerialDataSignal = pyqtSignal(object, object, object)
    killWorkerSignal = pyqtSignal()
    runButtonClickedSignal = pyqtSignal(object)

    def __init__(self, hubWindow):
        super().__init__(hubWindow, "Programmer")

        actSaveTextAs = QAction('Save &editor text', self, triggered=self.onTextSaveAs)
        actLoadText = QAction('&Load editor text', self, triggered=self.onTextLoad)
        self.fileMenu.addAction(actSaveTextAs)
        self.fileMenu.addAction(actLoadText)
        
        mainLayout = QVBoxLayout()

        self.worker = Worker()
        self.receiveCalibratedSerialDataSignal.connect(self.worker.receiveData)
        self.killWorkerSignal.connect(self.worker.kill)
        self.runButtonClickedSignal.connect(self.worker.runButtonPressed)
        QThreadPool.globalInstance().start(self.worker)
        self.worker.signals.sendDataSignal.connect(self.sendData)
        self.worker.signals.sendOutputSignal.connect(self.receiveOutput)
        self.worker.signals.forwardDataSignal.connect(self.forwardDataToHub)
        self.worker.signals.sendErrorSignal.connect(self.caughtError)
        self.worker.signals.stoppedRunningSignal.connect(self.stoppedRunning)

        self.editorTextEdit = QTextEdit()
        self.editorTextEdit.setObjectName("editorTextEditObj")
        self.editorTextEdit.setStyleSheet("#editorTextEditObj {color: #ffffff}")
        self.editorTextEdit.setTabStopDistance(20)
        self.editorTextEdit.setLineWrapMode(QTextEdit.NoWrap)
        self.highlight = PythonHighlighter(self.editorTextEdit.document())

        self.outputEditorTextEdit = QTextEdit()
        self.outputEditorTextEdit.setReadOnly(True)
        self.outputEditorTextEdit.setLineWrapMode(QTextEdit.NoWrap)
        self.outputEditorTextEdit.setVisible(False)

        graphSplitter = QSplitter(Qt.Vertical)
        graphSplitter.addWidget(self.editorTextEdit)
        graphSplitter.addWidget(self.outputEditorTextEdit)

        mainLayout.addWidget(graphSplitter)

        self.outputLayout = QVBoxLayout()
        mainLayout.addLayout(self.outputLayout)

        self.errorLabel = QLabel("t")
        self.errorLabel.setStyleSheet("color: red")
        self.errorLabel.hide()
        mainLayout.addWidget(self.errorLabel)

        self.runButton = QPushButton("Run")
        self.runButton.clicked.connect(self.startedRunning)

        self.loopButton = QPushButton("Loop")
        self.loopButton.clicked.connect(self.worker.loopButtonPressed)
        self.loopButton.setCheckable(True)

        self.stopButton = QPushButton("Stop")
        self.stopButton.clicked.connect(self.worker.stopButtonPressed)
        self.stopButton.setEnabled(False)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.runButton)
        controlLayout.addWidget(self.loopButton)
        controlLayout.addWidget(self.stopButton)
        mainLayout.addLayout(controlLayout)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def onTextSaveAs(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'Save current editor text to file', None, "*.txt", "", QFileDialog.DontUseNativeDialog)
        if fname == '': return False
        if fname.split(".")[-1] != "txt": fname += ".txt"
        QApplication.setOverrideCursor(Qt.WaitCursor)
        with open(fname, "w") as file:
            file.write(self.editorTextEdit.toPlainText())
        QApplication.restoreOverrideCursor()
        return True

    def onTextLoad(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'Open text from file', "", "*.txt", "", QFileDialog.DontUseNativeDialog)
        if fname != '' and os.path.isfile(fname):
            with open(fname, "r") as file:
                text = file.read()
                self.editorTextEdit.setPlainText(text)

    def startedRunning(self):
        self.runButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.errorLabel.hide()
        self.highlight.setEnableHighlighting(False)
        self.highlight.rehighlight()
        self.editorTextEdit.setStyleSheet("#editorTextEditObj {color: #999999}")
        self.runButtonClickedSignal.emit(self.editorTextEdit.toPlainText())

    def stoppedRunning(self):
        self.runButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.highlight.setEnableHighlighting(True)
        self.highlight.rehighlight()
        self.editorTextEdit.setStyleSheet("#editorTextEditObj {color: #ffffff}")

    def caughtError(self, error):
        self.errorLabel.setText(str(error))
        self.errorLabel.show()

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        self.receiveCalibratedSerialDataSignal.emit(serialParameters, data, dataInfo)

    def receiveOutput(self, text):
        if text == "CLEAR_OUTPUT_SIGNAL":
            self.outputEditorTextEdit.clear()
        else:
            self.outputEditorTextEdit.setVisible(True)
            self.outputEditorTextEdit.append(str(text))

    def sendData(self, data, ports: None):
        self.sendSerialData(data, ports)

    def forwardDataToHub(self, serialParameters: SerialParameters, data, dataInfo=None):
        self._hubWindow.printReceivedData(serialParameters, data, dataInfo)

    def onClosing(self):
        self.killWorkerSignal.emit()

    def save(self):
        tempSave = {
            "plainText": self.editorTextEdit.toPlainText()
        }
        return tempSave

    def load(self, data):
        self.editorTextEdit.setPlainText(data["plainText"])
