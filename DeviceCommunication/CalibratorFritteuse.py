import re
import time

from PyQt5.QtCore import QTimer
from SerialParameters import SerialParameters


class CalibratorFritteuse:
    def __init__(self, parent=None, port: str = ""):
        self.lastTempValue = 0.0
        self.newTempAvailable = False
        self.temperatureValues = {"values": [0.0], "times": [0.0]}
        self.lastSetPointTemp = 0.0
        self.newSetPointAvailable = False
        self.setPointTemps = {"values": [0.0], "times": [0.0]}
        self._maxGraphLength = 2000

        self.isTempControlActive = None
        self.newTempControlAvailable = False

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

        self._answerTimeoutTimer = QTimer()
        self._answerTimeoutTimer.timeout.connect(self.noAnswerReceived)
        self._answerTimeoutTimer.setInterval(self._answerTimeout)
        self._answerTimeoutTimer.setSingleShot(True)

    def askForTemp(self):
        self.sendMessage("{M01****\r\n")

    def setSetPointTemp(self, value: float):
        hexValue = format(int(value*100), 'x').upper().zfill(4)
        self.sendMessage("{M71" + hexValue + "\r\n")

    def setTempControl(self, b: bool):
        if b == True:
            self.sendMessage("{M140001\r\n")
        else:
            self.sendMessage("{M140000\r\n")

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        if self._port != "" and serialParameters.port.upper() != self._port.upper():
            return
        if serialParameters.readTextIndex != "read_line" or dataInfo["dataType"] != "RAW-Values" or type(data) != bytes:
            return
        data = data.decode()
        if not re.match(r"\{S[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]", data):
            return
        data = data.strip()

        self._answerTimeoutTimer.stop()
        self._isActiveCommunication = False

        addess = data[2:4]
        value = int(data[4:8], 16)

        if addess == "71":
            self.lastSetPointTemp = value/100
            self.newSetPointAvailable = True
            self.setPointTemps["values"].append(self.lastSetPointTemp)
            self.setPointTemps["times"].append(time.time()-self._startTime)
            self.setPointTemps["values"] = self.setPointTemps["values"][-self._maxGraphLength:]
            self.setPointTemps["times"] = self.setPointTemps["times"][-self._maxGraphLength:]
            if len(self.temperatureValues["values"]) > 0:
                self.temperatureValues["values"].append(self.temperatureValues["values"][-1])
                self.temperatureValues["times"].append(time.time()-self._startTime)
                self.temperatureValues["values"] = self.temperatureValues["values"][-self._maxGraphLength:]
                self.temperatureValues["times"] = self.temperatureValues["times"][-self._maxGraphLength:]
        elif addess == "01":
            self.lastTempValue = value / 100
            self.newTempAvailable = True
            self.temperatureValues["values"].append(self.lastTempValue)
            self.temperatureValues["times"].append(time.time()-self._startTime)
            self.temperatureValues["values"] = self.temperatureValues["values"][-self._maxGraphLength:]
            self.temperatureValues["times"] = self.temperatureValues["times"][-self._maxGraphLength:]
            if len(self.setPointTemps["values"]) > 0:
                self.setPointTemps["values"].append(self.setPointTemps["values"][-1])
                self.setPointTemps["times"].append(time.time()-self._startTime)
                self.setPointTemps["values"] = self.setPointTemps["values"][-self._maxGraphLength:]
                self.setPointTemps["times"] = self.setPointTemps["times"][-self._maxGraphLength:]
        elif addess == "14":
            self.isTempControlActive = True if value == 1 else False
            self.newTempControlAvailable = True

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
        timeout = self._answerTimeout if timeout < 0 else timeout
        maxBacklogSize = self._maxBacklogSize if maxBacklogSize < 0 else maxBacklogSize
        retryCount = self._retryCount if retryCount < 0 else retryCount

        if self._isActiveCommunication == True:
            if priority == 9999:
                self._messageBacklog.append({"message": message, "timeout": timeout, "maxBacklogSize": maxBacklogSize, "retryCount": retryCount, "senderID": senderID, "priority": max(priority, 0)})
            else:
                for index, m in enumerate(self._messageBacklog):
                    if m["priority"] > priority:
                        self._messageBacklog.insert(index, {"message": message, "timeout": timeout, "maxBacklogSize": maxBacklogSize, "retryCount": retryCount, "senderID": senderID, "priority": max(priority, 0)})
                        break
            self._messageBacklog = self._messageBacklog[:maxBacklogSize]
            return

        self._isActiveCommunication = True
        self._answerTimeoutTimer.start(timeout)
        self._currentCommMassage = {"message": message, "timeout": timeout, "maxBacklogSize": maxBacklogSize, "retryCount": retryCount, "senderID": senderID, "priority": max(priority, 0)}

        if self._port == "":
            self._parent.sendSerialData(message.encode('utf-8'))
        else:
            self._parent.sendSerialData(message.encode('utf-8'), [self._port])

