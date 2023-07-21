import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class FilterMenu(QMenu):
    connectActionTriggeredSignal = pyqtSignal(str)
    disconnectActionTriggeredSignal = pyqtSignal(str)

    def __init__(self, connectedPorts: list, parent=None):
        super(FilterMenu, self).__init__(parent)
        self.connectedPorts = connectedPorts
        self.activePorts = []
        self.activeKennung = []
        self.activeCalibration = []

        self.allKennung = ["KENNUNG-ALL"]

        self.setTitle("&Signal-Filter")

        # Port Filter Menu
        self.activePortMenu = self.addMenu("Active &Ports")

        action = QAction("COM-ALL", self)
        action.setCheckable(True)
        action.setChecked(True)
        action.triggered.connect(lambda: self.actionTriggeredEvent(self.activePorts, self.activePortMenu, "COM-ALL"))
        self.activePortMenu.addAction(action)
        self.activePorts.append("COM-ALL")

        self.addComAction = QAction("ADD-COM", self)
        self.addComAction.triggered.connect(self.addComActionPressed)
        self.activePortMenu.addAction(self.addComAction)

        # Kennung Filter Menu
        self.activeKennungMenu = self.addMenu("Active &Kennung")

        action = QAction("KENNUNG-ALL", self)
        action.setCheckable(True)
        action.setChecked(True)
        action.triggered.connect(lambda: self.actionTriggeredEvent(self.activeKennung, self.activeKennungMenu, "KENNUNG-ALL"))
        self.activeKennungMenu.addAction(action)
        self.activeKennung.append("KENNUNG-ALL")

        self.addKennungAction = QAction("ADD-Kennung", self)
        self.addKennungAction.triggered.connect(self.addKennungActionPressed)
        self.activeKennungMenu.addAction(self.addKennungAction)

        # Calibration Filter Menu
        self.activeCalibrationMenu = self.addMenu("Show &Calibration")

        rawAction = QAction("RAW-Values", self)
        rawAction.setCheckable(True)
        rawAction.setChecked(True)
        rawAction.triggered.connect(lambda: self.actionTriggeredEvent(self.activeCalibration, self.activeCalibrationMenu, ""))
        self.activeCalibrationMenu.addAction(rawAction)
        self.activeCalibration.append("RAW-Values")

        calAction = QAction("CALIBRATED-Values", self)
        calAction.setCheckable(True)
        calAction.setChecked(True)
        calAction.triggered.connect(lambda: self.actionTriggeredEvent(self.activeCalibration, self.activeCalibrationMenu, ""))
        self.activeCalibrationMenu.addAction(calAction)
        self.activeCalibration.append("CALIBRATED-Values")

    def showEvent(self, QEvent):
        self.activePortMenu.removeAction(self.addComAction)
        for p in self.connectedPorts:
            if any(x.text() == p.port for x in self.activePortMenu.actions()):
                continue
            action = QAction(p.port, self)
            action.setCheckable(True)
            action.triggered.connect(lambda: self.actionTriggeredEvent(self.activePorts, self.activePortMenu, "COM-ALL"))
            self.activePortMenu.addAction(action)
        self.activePortMenu.addAction(self.addComAction)

        self.activeKennungMenu.removeAction(self.addKennungAction)
        self.activeKennungMenu.addAction(self.addKennungAction)

    def actionTriggeredEvent(self, activeList, menu: QMenu, s: str):
        if self.sender().isChecked():
            if self.sender().text() not in activeList:
                activeList.append(self.sender().text())
        else:
            if self.sender().text() in activeList:
                activeList.remove(self.sender().text())

        if self.sender().text() == s and self.sender().isChecked():
            for act in menu.actions():
                if act.text() != s and act.text() in activeList:
                    act.setChecked(False)
                    activeList.remove(act.text())
        if self.sender().text() != s and self.sender().isChecked():
            for act in menu.actions():
                if act.text() == s and act.text() in activeList:
                    act.setChecked(False)
                    activeList.remove(act.text())

    def addComActionPressed(self):
        text, ok = QInputDialog.getText(self, 'New COM Filter', 'Enter new COM filter:')
        if text and text != "":
                action = QAction(text.upper(), self)
                action.setCheckable(True)
                action.setChecked(True)
                action.triggered.connect(lambda: self.actionTriggeredEvent(self.activePorts, self.activePortMenu, "COM-ALL"))
                self.activePortMenu.addAction(action)
                self.activePorts.append(text.upper())
                for act in self.activePortMenu.actions():
                    if act.text() == "COM-ALL" and act.text() in self.activePorts:
                        act.setChecked(False)
                        self.activePorts.remove(act.text())

    def addKennungActionPressed(self):
        text, ok = QInputDialog.getText(self, 'New Kennung Filter', 'Enter new Kennung filter:')
        if text and text != "":
            action = QAction(text.lower(), self)
            action.setCheckable(True)
            action.setChecked(True)
            action.triggered.connect(lambda: self.actionTriggeredEvent(self.activeKennung, self.activeKennungMenu, "KENNUNG-ALL"))
            self.activeKennungMenu.addAction(action)
            self.allKennung.append(text)
            self.activeKennung.append(text)
            for act in self.activeKennungMenu.actions():
                if act.text() == "KENNUNG-ALL" and act.text() in self.activeKennung:
                    act.setChecked(False)
                    self.activeKennung.remove(act.text())

    def addKennungWithoutPressed(self, text: str):
        action = QAction(text.lower(), self)
        action.setCheckable(True)
        action.triggered.connect(lambda: self.actionTriggeredEvent(self.activeKennung, self.activeKennungMenu, "KENNUNG-ALL"))
        self.activeKennungMenu.addAction(action)
        self.allKennung.append(text)

    def serialize(self):
        allPorts = []
        for act in self.activePortMenu.actions():
            allPorts.append(act.text())
        allKennung = []
        for act in self.activeKennungMenu.actions():
            allKennung.append(act.text())
        allCalibration = ["RAW-Values", "CALIBRATED-Values"]

        return {
            "_activePorts": self.activePorts,
            "_allPorts": allPorts,
            "_activeKennung": self.activeKennung,
            "_allKennung": allKennung,
            "_activeCalibration": self.activeCalibration,
            "_allCalibration": allCalibration,
        }

    def deserialize(self, data):
        for port in data["_allPorts"]:
            if any(x.text() == port for x in self.activePortMenu.actions()):
                continue
            action = QAction(port, self)
            action.setCheckable(True)
            action.triggered.connect(lambda: self.actionTriggeredEvent(self.activePorts, self.activePortMenu, "COM-ALL"))
            self.activePortMenu.addAction(action)

        for act in self.activePortMenu.actions():
            act.setChecked(False)
            if act.text() in self.activePorts:
                self.activePorts.remove(act.text())
            if act.text() in data["_activePorts"]:
                act.setChecked(True)
                self.activePorts.append(act.text())

        for kennung in data["_allKennung"]:
            if any(x.text() == kennung for x in self.activeKennungMenu.actions()):
                continue
            action = QAction(kennung, self)
            action.setCheckable(True)
            action.triggered.connect(lambda: self.actionTriggeredEvent(self.activeKennung, self.activeKennungMenu, "KENNUNG-ALL"))
            self.activeKennungMenu.addAction(action)
            self.allKennung.append(kennung)

        for act in self.activeKennungMenu.actions():
            act.setChecked(False)
            if act.text() in self.activeKennung:
                self.activeKennung.remove(act.text())
            if act.text() in data["_activeKennung"]:
                act.setChecked(True)
                self.activeKennung.append(act.text())

        for act in self.activeCalibrationMenu.actions():
            act.setChecked(False)
            if act.text() in self.activeCalibration:
                self.activeCalibration.remove(act.text())
            if act.text() in data["_activeCalibration"]:
                act.setChecked(True)
                self.activeCalibration.append(act.text())
