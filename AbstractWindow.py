import binascii
import json
import os
import sys
from typing import Union

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QComboBox, QFileDialog, QMenu, QAction
from SerialParameters import SerialParameters
from FilterMenu import FilterMenu


class PortCombobox(QComboBox):
    def __init__(self, connectedPorts: list):
        super().__init__()
        self.connectedPorts = connectedPorts

        self.addItem("COM-ALL")
        for p in self.connectedPorts:
            self.addItem(p.port)
        self.setEditable(True)
        self.adjustSize()

    def showPopup(self):
        for p in self.connectedPorts:
            if self.findText(p.port) == -1:
                self.addItem(p.port)
        super().showPopup()


class AbstractWindow(QMainWindow):
    sendSerialWriteSignal = pyqtSignal(str, object)
    killSerialConnectionSignal = pyqtSignal(str)
    startSerialRecordSignal = pyqtSignal(str, str, str)
    stopSerialRecordSignal = pyqtSignal(str)
    writeToFileSignal = pyqtSignal(str, str, str, str)

    def __init__(self, hubWindow, windowType: str):
        super().__init__()

        self._windowType = windowType
        self._hubWindow = hubWindow

        fileMenu = QMenu("&File", self)
        actSaveAs = QAction('&Save window layout', self, triggered=self.onFileSaveAs)
        actOpen = QAction('&Open window layout', self, triggered=self.onFileOpen)
        fileMenu.addAction(actSaveAs)
        fileMenu.addAction(actOpen)
        self.menuBar().addMenu(fileMenu)

        self.menuFilter = FilterMenu(self._hubWindow.connectedPorts, self)
        self.menuBar().addMenu(self.menuFilter)

        windowMenu = QMenu("&Window", self)
        self.actFrameless = QAction('&Frameless', self, triggered=self.onFrameless)
        self.actFrameless.setCheckable(True)
        self.actFrameless.setChecked(False)
        self.actStayOnTop = QAction('&StayOnTop', self, triggered=self.onStayOnTop)
        self.actStayOnTop.setCheckable(True)
        self.actStayOnTop.setChecked(False)
        windowMenu.addAction(self.actFrameless)
        windowMenu.addAction(self.actStayOnTop)
        self.menuBar().addMenu(windowMenu)

        self.initUI()
        self.show()
        self.adjustSize()

    def initUI(self):
        self.setWindowTitle(self._windowType)

    def serialize(self) -> dict:
        return {
            "_windowType": self._windowType,
            "_windowSize": [self.size().width(), self.size().height()],
            "_windowPosition": [self.pos().x(), self.pos().y()],
            "_filterMenu": self.menuFilter.serialize(),
            "_windowSaveInfo": self.save(),
            "_windowFlags": [self.actFrameless.isChecked(), self.actStayOnTop.isChecked()]
        }

    def save(self):
        pass

    def deserialize(self, data: dict):
        if data['_windowType'] != self._windowType:
            print("Not the right save file! Window type: " + str(data['_windowType']))
            return False

        self.resize(data['_windowSize'][0], data['_windowSize'][1])

        # Check if Window is outside of screen:    Auskommentiert, weil unnütz für die meisten Fälle
        #if (QApplication.primaryScreen().size().width() < data['_windowPosition'][0] + data['_windowSize'][0] or data['_windowPosition'][0] < 0 or QApplication.primaryScreen().size().height() < data['_windowPosition'][1] + data['_windowSize'][1] or data['_windowPosition'][1] < 0) and self.returnMsgBoxAnswerYesNo("Out Of Screen", "Window \"" + str(self._windowType) + "\" is out of screen!\nDo you want to move it inside the screen?") == QMessageBox.Yes:
        #    self.move(max(0, min(data['_windowPosition'][0], QApplication.primaryScreen().size().width() - data['_windowSize'][0])), max(0, min(data['_windowPosition'][1],QApplication.primaryScreen().size().height() - data['_windowSize'][1])))
        #else:
        #    self.move(data['_windowPosition'][0], data['_windowPosition'][1])
        self.move(data['_windowPosition'][0], data['_windowPosition'][1])

        self.menuFilter.deserialize(data["_filterMenu"])

        self.actFrameless.setChecked(data['_windowFlags'][0])
        self.actStayOnTop.setChecked(data['_windowFlags'][1])
        self.onFrameless(data['_windowFlags'][0])
        self.onStayOnTop(data['_windowFlags'][1])

        self.load(data['_windowSaveInfo'])

        return True

    def load(self, data):
        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self._hubWindow.deleteWindowFromList(self)
        return None

    def onFileSaveAs(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'Save current window layout to file', None, "*.json", "", QFileDialog.DontUseNativeDialog)
        if fname == '': return False
        if fname.split(".")[-1] != "json": fname += ".json"
        QApplication.setOverrideCursor(Qt.WaitCursor)
        with open(fname, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        QApplication.restoreOverrideCursor()
        return True

    def onFileOpen(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file', "", "*.json", "", QFileDialog.DontUseNativeDialog)
        if fname != '' and os.path.isfile(fname):
            with open(fname, "r") as file:
                raw_data = file.read()
                try:
                    if sys.version_info >= (3, 9):
                        data = json.loads(raw_data)
                    else:
                        data = json.loads(raw_data, encoding='utf-8')
                    self.deserialize(data)
                except json.JSONDecodeError:
                    raise TypeError("%s is not a valid JSON file" % os.path.basename(fname))
                except Exception as e:
                    print(e)

    def onFrameless(self, checked: bool):
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        self.show()

    def onStayOnTop(self, checked: bool):
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def returnMsgBoxAnswerYesNo(self, title: str = "Message", text: str = ""):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(title)
        dlg.setText(text)
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        return dlg.exec()

    def madeSerialConnection(self, serialParameters: SerialParameters):
        pass

    def lostSerialConnection(self, serialParameters: SerialParameters):
        pass

    def receiveCalibratedSerialData(self, serialParameters: SerialParameters, data, dataInfo):
        kennung = ""
        try:
            kennung = binascii.hexlify(serialParameters.Kennbin).decode("utf-8")
        except:
            pass
            #print("Kennung nicht vorhanden!")
        if kennung not in self.menuFilter.allKennung and kennung != "":
            #print("new Kennung: ", kennung)
            self.menuFilter.addKennungWithoutPressed(kennung)
        if any(port in self.menuFilter.activePorts for port in [serialParameters.port, "COM-ALL"]):
            if kennung == "" or (any(kenn in self.menuFilter.activeKennung for kenn in [str(serialParameters.Kennung), kennung, "KENNUNG-ALL"])):
                if dataInfo["dataType"] in self.menuFilter.activeCalibration:
                    self.receiveData(serialParameters, data, dataInfo)

    def findCalibratedDataByUUID(self, data, dataInfo, UUID: str):
        if dataInfo["dataType"] == "CALIBRATED-Values":
            if data.get("UUID") is not None:
                if UUID in data["UUID"]:
                    index = data["UUID"].index(UUID)
                    return data["DATA"][index]
        return None

    def findCalibratedDataByKeyValue(self, data, dataInfo, key: str, value):
        if dataInfo["dataType"] == "CALIBRATED-Values":
            listDatas = self._hubWindow.measuringPointListFiles
            for listData in listDatas:
                if key in listData["DATA"].keys():
                    if value in listData["DATA"][key]:
                        return data["DATA"][listData["DATA"][key].index(value)]
            return None

    def findUUIDDataByKeyValue(self, key: str, value):
        listDatas = self._hubWindow.measuringPointListFiles
        for listData in listDatas:
            if key in listData["DATA"].keys():
                if value in listData["DATA"][key]:
                            return listData["DATA"]["UUID"][listData["DATA"][key].index(value)]
        return None

    def findIndexByUUID(self, UUID: str):
        listDatas = self._hubWindow.measuringPointListFiles
        for listData in listDatas:
            if "UUID" in listData["DATA"].keys():
                if UUID in listData["DATA"]["UUID"]:
                    return listData["DATA"]["UUID"].index(UUID)
        return None

    def findMeasuringPointInfoByUUID(self, UUID: str):
        listDatas = self._hubWindow.measuringPointListFiles
        for listData in listDatas:
            index = self.findIndexByUUID(UUID)
            if index is not None:
                temp = {}
                for key in listData["DATA"].keys():
                    temp[key] = listData["DATA"][key][index]
                return temp
        return None

    def failedSendSerialData(self, serialParameters: SerialParameters, data):
        pass

    def startedSerialRecording(self, serialParameters: SerialParameters):
        pass

    def stopSerialRecording(self, serialParameters: SerialParameters):
        pass

    def sendSerialData(self, data):
        self.sendSerialWriteSignal.emit("|".join(self.menuFilter.activePorts), data)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        pass
