import re
import time

from PyQt5.QtCore import QPoint, Qt, QRunnable, pyqtSlot, QThreadPool, QProcess, QRegExp, pyqtSignal, QObject
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, \
    QGridLayout, QTextEdit, QSplitter
from PyQt5.QtGui import QPixmap, QFont, QTextDocument, QSyntaxHighlighter, QColor, QTextCharFormat, QCloseEvent
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from time import sleep


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
        self.globalPorts = None
        self.globalTimeout = None
        self.globalRetry = 0

        self.lastData = None
    @pyqtSlot()
    def run(self):
        while not self.is_killed:
            if self.running == True:
                #try:
                self.initVars()
                exec(self.program)
                #except Exception as inst:
                #    self.signals.sendErrorSignal.emit(inst)
                #    self.running = False
                #    self.signals.stoppedRunningSignal.emit()

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
        self.globalDevice = None
        self.globalPorts = None
        self.globalTimeout = None
        self.globalRetry = 0

    def query(self, message: str = None, device: str = None, command: str = None, value=None, unit=None, ports=None, timeout: float = None, retry: int = None):
        self.lastData = None
        startTime = time.time()

        # apply global variables if necessary
        device = self.globalDevice if device is None else device
        ports = self.globalPorts if ports is None else ports
        timeout = self.globalTimeout if timeout is None else timeout
        retry = self.globalRetry if retry is None else retry

        if device == "Fritteuse":
            if command.lower() in ["t", "temp", "temperature"]:
                message = "{M01****\r\n"
            elif command.lower() in ["setpointtemp", "setpointtemperature", "set", "setpoint", "soll", "sollwert", "setzesollwert"]:
                message = "{M71" + format(int(value * 100), 'x').upper().zfill(4) + "\r\n" if type(value) in [int, float] else message
            elif command.lower() in ["tempcontrol", "temperaturecontrol", "settempcontrol", "settemperaturecontrol", "settempcon", "control"]:
                message = "{M14000" + str(int(value)) + "\r\n" if type(value) in [bool] else message

        if message is not None:
            if ports is not None:
                if type(ports) == str:
                    ports = [ports]
            self.sendData(message, ports)
        else:
            return None

        # Waiting for answer
        while True:
            # Timeout occurred
            if timeout is not None:
                if time.time() - startTime >= timeout:
                    if retry > 0:
                        return self.query(message, device, command, value, unit, ports, timeout, retry-1)
                    else:
                        return None
            if self.lastData is not None:

                # No device specified
                if device is None:
                    return self.lastData

                # Keithley2010 specified
                elif device == "Fritteuse":
                    if re.match(r"\{S[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]", self.lastData.decode()):
                        return self.lastData

                self.lastData = None
            sleep(0.05)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        self.lastData = data

    def sendData(self, data: str, ports: list = None):
        self.signals.sendDataSignal.emit(data.encode('utf-8'), ports)

    def sendOutput(self, text):
        self.signals.sendOutputSignal.emit(text)

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
        
        mainLayout = QVBoxLayout()

        self.worker = Worker()
        self.receiveCalibratedSerialDataSignal.connect(self.worker.receiveData)
        self.killWorkerSignal.connect(self.worker.kill)
        self.runButtonClickedSignal.connect(self.worker.runButtonPressed)
        QThreadPool.globalInstance().start(self.worker)
        self.worker.signals.sendDataSignal.connect(self.sendData)
        self.worker.signals.sendOutputSignal.connect(self.receiveOutput)
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
        self.outputEditorTextEdit.setVisible(True)
        self.outputEditorTextEdit.append(str(text))

    def sendData(self, data, ports: None):
        self.sendSerialData(data, ports)

    def onClosing(self):
        self.killWorkerSignal.emit()

    def save(self):
        tempSave = {
            "plainText": self.editorTextEdit.toPlainText()
        }
        return tempSave

    def load(self, data):
        self.editorTextEdit.setPlainText(data["plainText"])
