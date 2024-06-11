import re
import time

from PyQt5.QtCore import QTimer
from SerialParameters import SerialParameters


class CTD9300:
    def __init__(self, parent=None, port: str = ""):
        self.lastTempValue = 0.0
        self.newTempAvailable = False
        self.temperatureValues = {"values": [0.0], "times": [0.0]}

        self.lastPTempValue = 0.0
        self.newPTempAvailable = False
        self.pTemperatureValues = {"values": [0.0], "times": [0.0]}

        self.lastRTempValue = 0.0
        self.newRTempAvailable = False
        self.rTemperatureValues = {"values": [0.0], "times": [0.0]}

        self.lastSetPointTemp = 0.0
        self.newSetPointAvailable = False
        self.setPointTemps = {"values": [0.0], "times": [0.0]}

        self._maxGraphLength = 2000

        self.currentControlStatus = None
        self.kennung = None

        self.isTempControlActive = None
        self.newTempControlAvailable = False

        # internal variables
        self._parent = parent
        self._port = port
        self._isActiveCommunication = False
        self._retryCount = 0
        self._answerTimeout = 50
        self._maxBacklogSize = 0
        self._messageBacklog = []
        self._currentCommMassage = {}
        self._startTime = time.time()

        #self._answerTimeoutTimer = QTimer()
        #self._answerTimeoutTimer.timeout.connect(self.noAnswerReceived)
        #self._answerTimeoutTimer.setInterval(self._answerTimeout)
        #self._answerTimeoutTimer.setSingleShot(True)

        #self._workOnBacklogTimer = QTimer()
        #self._workOnBacklogTimer.timeout.connect(self.workBacklog)
        #self._workOnBacklogTimer.setInterval(100)
        #self._workOnBacklogTimer.start()

        self._setpointTimer = QTimer()
        self._setpointTimer.timeout.connect(self.getSetPointTemp)
        self._setpointTimer.setInterval(1000)
        self._setpointTimer.start()

    def setSetPointTemp(self, value: float):
        self.sendMessage("\x02" + "S" + str(value) + "\x03")

    def setTempControl(self, b: bool):
        value = "1" if b else "0"
        self.sendMessage("\x02" + "O" + value + "\x03")

    def getSetPointTemp(self):
        self.sendMessage("\x02" + "s" + "\x03")

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        if self._port != "" and serialParameters.port.upper() != self._port.upper():
            return

        if serialParameters.readTextIndex != "read_until_ASCII" or dataInfo["dataType"] != "RAW-Values" or type(data) != bytes:
            return
        data = data.decode('ascii', 'ignore').strip("\x02").strip("\x03").strip()
        data = data.replace(",", ".")

        identifier = data[0]

        if identifier == "m":
            if len(data.split("R")) == 2:
                self.lastRTempValue = float(data.split("R")[1]) if "!" not in data.split("R")[1] else self.lastRTempValue
                self.newRTempAvailable = True
                data = data.split("R")[0]
            if len(data.split("P")) == 2:
                self.lastPTempValue = float(data.split("P")[1]) if "!" not in data.split("P")[1] else self.lastPTempValue
                self.newPTempAvailable = True
                data = data.split("P")[0]
            if len(data.split("B")) == 2:
                self.currentControlStatus = data.split("B")[1][0]
                self.lastTempValue = float(data.split("B")[1][1:]) if "!" not in data.split("B")[1][1:] else self.lastTempValue
                self.newTempAvailable = True
            self.appendValues()
        if identifier == "s":
            self.lastSetPointTemp = float(data[1:]) if "!" not in data[1:] else self.lastSetPointTemp
            self.newSetPointAvailable = True
            self.appendValues()

    def appendValues(self):
        self.temperatureValues["values"].append(self.lastTempValue)
        self.temperatureValues["times"].append(time.time() - self._startTime)
        self.temperatureValues["values"] = self.temperatureValues["values"][-self._maxGraphLength:]
        self.temperatureValues["times"] = self.temperatureValues["times"][-self._maxGraphLength:]

        self.pTemperatureValues["values"].append(self.lastPTempValue)
        self.pTemperatureValues["times"].append(time.time() - self._startTime)
        self.pTemperatureValues["values"] = self.pTemperatureValues["values"][-self._maxGraphLength:]
        self.pTemperatureValues["times"] = self.pTemperatureValues["times"][-self._maxGraphLength:]

        self.rTemperatureValues["values"].append(self.lastRTempValue)
        self.rTemperatureValues["times"].append(time.time() - self._startTime)
        self.rTemperatureValues["values"] = self.rTemperatureValues["values"][-self._maxGraphLength:]
        self.rTemperatureValues["times"] = self.rTemperatureValues["times"][-self._maxGraphLength:]

        self.setPointTemps["values"].append(self.lastSetPointTemp)
        self.setPointTemps["times"].append(time.time() - self._startTime)
        self.setPointTemps["values"] = self.setPointTemps["values"][-self._maxGraphLength:]
        self.setPointTemps["times"] = self.setPointTemps["times"][-self._maxGraphLength:]

    def noAnswerReceived(self):
        self._isActiveCommunication = False
        if self._currentCommMassage["retryCount"] > 0:
            self._currentCommMassage["retryCount"] = self._currentCommMassage["retryCount"] - 1
            self.sendMessage(self._currentCommMassage["message"], self._currentCommMassage["timeout"], self._currentCommMassage["maxBacklogSize"], self._currentCommMassage["retryCount"], self._currentCommMassage["senderID"], self._currentCommMassage["priority"])
            return
        if len(self._messageBacklog) > 0:
            c = self._messageBacklog.pop(0)
            self.sendMessage(c["message"], c["timeout"], c["maxBacklogSize"], c["retryCount"], c["senderID"], c["priority"])

    def sendMessage(self, message: str, timeout: int = -1, maxBacklogSize: int = -1, retryCount: int = -1, senderID: str = "", priority: int = 9999):
        if self._port == "":
            self._parent.sendSerialData(message.encode('utf-8'))
        else:
            self._parent.sendSerialData(message.encode('utf-8'), [self._port])

    def onClosing(self):
        self._setpointTimer.stop()
        #self._answerTimeoutTimer.stop()
        del self

