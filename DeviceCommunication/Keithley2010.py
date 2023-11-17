import re
import time
from time import sleep

from PyQt5.QtCore import QTimer
from SerialParameters import SerialParameters


class Keithley2010:
    def __init__(self, parent=None, port: str = ""):
        self.lastKeithleyValues = []
        self.tempLastKeithleyValues = []
        self.newKeithleyAvailable = False

        # internal variables
        self._parent = parent
        self._port = port
        self._isActiveCommunication = False
        self._retryCount = 0
        self._answerTimeout = 0
        self._maxBacklogSize = 0
        self._messageBacklog = []
        self._currentCommMassage = {}
        self._startTime = time.time()

        self._initMessageCounter = -1
        self._initMessages = ["*RST", "*CLS", "INIT:CONT OFF", "ABORT"]
        self.isInitDone = False

        self._initTimer = QTimer()
        self._initTimer.timeout.connect(self.initKeithley)
        self._initTimer.setInterval(200)

        self._askForMessageCounter = -1
        self._askForMessages = []
        self._askForKeithleyRange = []
        self._askForKeithleyChannel = []
        self._askForKeithleyFunc = []

        self._askForTimer = QTimer()
        self._askForTimer.timeout.connect(self.askForKeithleyTimerFunc)
        self._askForTimer.setInterval(100)

        self._answerTimeoutTimer = QTimer()
        self._answerTimeoutTimer.timeout.connect(self.noAnswerReceived)
        self._answerTimeoutTimer.setInterval(self._answerTimeout)
        self._answerTimeoutTimer.setSingleShot(True)

    def initKeithley(self):
        if not self._initTimer.isActive():
            self._initMessageCounter = 0
            self._initTimer.start()
        elif self._initMessageCounter >= len(self._initMessages):
            self._initTimer.stop()
            self.isInitDone = True
        else:
            self._parent.sendSerialData((self._initMessages[self._initMessageCounter] + "\r\n").encode('utf-8'), [self._port])
            self._initMessageCounter += 1

    def askForKeithley(self, channel: list, func: list, measurementRange: list):
        if not self._askForTimer.isActive():
            self.tempLastKeithleyValues = []

            self._askForKeithleyChannel = channel
            self._askForKeithleyFunc = func
            self._askForKeithleyRange = measurementRange
            self._askForMessageCounter = 0

            self._askForMessages = []
            for i in range(0, len(channel)):
                self._askForMessages.append(":SENS:FUNC \"" + str(func[i]) + "\"")
                self._askForMessages.append(":SENS:FRES:RANG " + str(measurementRange[i]))
                self._askForMessages.append("ROUTE:CLOSE (@" + str(channel[i]) + ")")
                self._askForMessages.append(":READ?")

            self._askForTimer.start()

        # self.sendMessage("*RST\r\n")
        # self.sendMessage("*CLS\r\n")
        # self.sendMessage("INIT:CONT OFF\r\n")
        # self.sendMessage("ABORT\r\n")
        # self.sendMessage(":SENS:FUNC \"FRES\"\r\n")
        # self.sendMessage(":SENS:FRES:RANG 10000\r\n")
        # self.sendMessage("ROUTE:CLOSE (@1)\r\n")
        # self.sendMessage(":READ?\r\n")
        #self._parent.sendSerialData("*RST\r\n".encode('utf-8'), [self._port])
        #self._parent.sendSerialData("*CLS\r\n".encode('utf-8'), [self._port])
        #self._parent.sendSerialData("INIT:CONT OFF\r\n".encode('utf-8'), [self._port])
        #self._parent.sendSerialData("ABORT\r\n".encode('utf-8'), [self._port])
        #self._parent.sendSerialData(":SENS:FUNC \"FRES\"\r\n".encode('utf-8'), [self._port])
        #self._parent.sendSerialData(":SENS:FRES:RANG 10000\r\n".encode('utf-8'), [self._port])
        #for channel in range(1, 5):
        #    command = "ROUTE:CLOSE (@" + str(channel) + ")\r\n"
        #    self._parent.sendSerialData(command.encode('utf-8'), [self._port])
        #    self._parent.sendSerialData(":READ?\r\n".encode('utf-8'), [self._port])

    def askForKeithleyTimerFunc(self):
        if self._askForMessageCounter >= len(self._askForMessages):
            self._askForTimer.stop()
            if len(self._askForKeithleyChannel) != len(self.tempLastKeithleyValues):
                self.askForKeithley(self._askForKeithleyChannel, self._askForKeithleyFunc, self._askForKeithleyRange)
                return
            else:
                self.lastKeithleyValues = self.tempLastKeithleyValues
                self.newKeithleyAvailable = True
        else:
            self._parent.sendSerialData((self._askForMessages[self._askForMessageCounter] + "\r\n").encode('utf-8'),
                                        [self._port])
            self._askForMessageCounter += 1

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        if self._port != "" and serialParameters.port.upper() != self._port.upper():
            return
        if serialParameters.readTextIndex != "read_line" or dataInfo["dataType"] != "RAW-Values" or type(data) != bytes:
            return
        data = data.decode()
        if not re.match(r"[+,-][0-9]*[.][0-9]*E[+,-][0-9]*.*", data):
            return
        data = data.strip()

        self._answerTimeoutTimer.stop()
        self._isActiveCommunication = False

        value = float(re.findall("[+,-][0-9]*[.][0-9]*E[+,-][0-9]*", data)[0])

        self.tempLastKeithleyValues.append(value)

    def noAnswerReceived(self):
        self._isActiveCommunication = False
        if self._currentCommMassage["retryCount"] > 0:
            self._currentCommMassage["retryCount"] = self._currentCommMassage["retryCount"] - 1
            self.sendMessage(self._currentCommMassage["message"], self._currentCommMassage["timeout"],
                             self._currentCommMassage["maxBacklogSize"], self._currentCommMassage["retryCount"],
                             self._currentCommMassage["senderID"], self._currentCommMassage["priority"])
            return
        if len(self._messageBacklog) > 0:
            c = self._messageBacklog.pop(0)
            self.sendMessage(c["message"], c["timeout"], c["maxBacklogSize"], c["retryCount"], c["senderID"],
                             c["priority"])

    def sendMessage(self, message: str, timeout: int = -1, maxBacklogSize: int = -1, retryCount: int = -1,
                    senderID: str = "", priority: int = 9999):
        timeout = self._answerTimeout if timeout < 0 else timeout
        maxBacklogSize = self._maxBacklogSize if maxBacklogSize < 0 else maxBacklogSize
        retryCount = self._retryCount if retryCount < 0 else retryCount

        if self._isActiveCommunication == True:
            if priority == 9999:
                self._messageBacklog.append(
                    {"message": message, "timeout": timeout, "maxBacklogSize": maxBacklogSize, "retryCount": retryCount,
                     "senderID": senderID, "priority": max(priority, 0)})
            else:
                for index, m in enumerate(self._messageBacklog):
                    if m["priority"] > priority:
                        self._messageBacklog.insert(index, {"message": message, "timeout": timeout,
                                                            "maxBacklogSize": maxBacklogSize, "retryCount": retryCount,
                                                            "senderID": senderID, "priority": max(priority, 0)})
                        break
            self._messageBacklog = self._messageBacklog[:maxBacklogSize]
            return

        self._isActiveCommunication = True
        self._answerTimeoutTimer.start(timeout)
        self._currentCommMassage = {"message": message, "timeout": timeout, "maxBacklogSize": maxBacklogSize,
                                    "retryCount": retryCount, "senderID": senderID, "priority": max(priority, 0)}

        if self._port == "":
            self._parent.sendSerialData(message.encode('utf-8'))
        else:
            self._parent.sendSerialData(message.encode('utf-8'), [self._port])
