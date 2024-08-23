from random import randint

from UsefulFunctions import strToIntElseNone, strToFloatElseNone

import binascii
import json
import time

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, \
    QTableWidget, QHeaderView, QTableWidgetItem, QSpinBox, QMessageBox, QSplitter, QAction
from PyQt5.QtCore import Qt
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from pyqtgraph import PlotWidget, plot, mkPen
from numpy import polyfit


class GraphLine:
    def __init__(self,startTime: float = 0):
        self.startTime = startTime
        self.x = []
        self.y = []
        self.dataLine = None
        self.dataCounter = 0

        self.maxLength = 200

    def appendDataPoint(self, y: float, x: float = None):
        if self.dataLine is None:
            return
        if x is None:
            x = time.time() - self.startTime
        elif x == -1:
            self.dataCounter += 1
            x = self.dataCounter
        if len(self.x) > self.maxLength > 0:
            self.x = self.x[-self.maxLength:]
            self.y = self.y[-self.maxLength:]
            self.x.append(x)
            self.y.append(y)
        else:
            self.x.append(x)
            self.y.append(y)
        self.dataLine.setData(self.x, self.y)


class WindowRawDataGraph(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "RawDataGraph")

        self.filterList = []

        self.graphLines = {}
        self.dataCounter = 0
        self.graphStartTime = time.time()

        self.graphWidget = PlotWidget()
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground(None)
        self.graphWidget.addLegend()

        self.errorLabel = QLabel("Wrong input! No correct json format or not a list!")
        self.errorLabel.setEnabled(False)
        self.errorLabel.setStyleSheet("QLabel { color: red }")
        self.errorLabel.hide()

        self.dataFilterLineEdit = QLineEdit()
        self.dataFilterLineEdit.setPlaceholderText("123 or [123, 456] or [\"AABB-123\", \"AABB-456\"]")
        self.dataFilterLineEdit.textChanged.connect(self.dataFilterChanged)

        #maxDataPointsLabel = QLabel("Max Data Points:")

        self.maxDataCountSpinBox = QSpinBox()
        self.maxDataCountSpinBox.setRange(1, 9999)
        self.maxDataCountSpinBox.setValue(200)
        self.maxDataCountSpinBox.editingFinished.connect(self.maxDataCountChanged)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.dataFilterLineEdit)
        #horizontalLayout.addWidget(maxDataPointsLabel)
        horizontalLayout.addWidget(self.maxDataCountSpinBox)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.graphWidget)
        mainLayout.addWidget(self.errorLabel)
        mainLayout.addLayout(horizontalLayout)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def dataFilterChanged(self):
        try:
            tempFilter = json.loads(self.dataFilterLineEdit.text())
            if type(tempFilter) in [int, list]:
                self.errorLabel.hide()

                if type(tempFilter) == int:
                    tempFilter = [tempFilter]
                self.filterList = tempFilter

                for index in range(0, len(self.filterList)):
                    self.filterList[index] = str(self.filterList[index]).upper()

                delKeyList = []
                for key in self.graphLines.keys():
                    if key not in self.filterList:
                        delKeyList.append(key)
                for key in delKeyList:
                    self.graphWidget.removeItem(self.graphLines[key].dataLine)
                    self.graphLines[key].dataLine.clear()
                    del self.graphLines[key]

                for filter in self.filterList:
                    if filter not in self.graphLines.keys():
                        pen = mkPen(color=QColor(randint(0, 255), randint(0, 255), randint(0, 255)))
                        self.graphLines[filter] = GraphLine(self.graphStartTime)
                        self.graphLines[filter].dataLine = self.graphWidget.plot([], [], pen=pen, name=filter)
                        self.graphLines[filter].maxLength = self.maxDataCountSpinBox.value()


        except Exception as e:
            self.errorLabel.show()

    def maxDataCountChanged(self):
        for key in self.graphLines.keys():
            self.graphLines[key].maxLength = self.maxDataCountSpinBox.value()

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        if dataInfo["dataType"] != "RAW-Values":
            return
        if serialParameters.readTextIndex == "read_WU_device":
            kennung = binascii.hexlify(serialParameters.Kennbin).decode("utf-8").upper()
        else:
            try:
                data = data.decode("utf-8").strip().replace(" ", "").replace(":", ";").split(";")
            except:
                data = data.strip().replace(" ", "").replace(":", ";").split(";")
            kennung = ""

        for key in self.graphLines.keys():
            name = key.split("-")
            if len(name) == 1:
                number = strToIntElseNone(name[0])
                if number is not None:
                    if number >= 0 and number < len(data):
                        if serialParameters.readTextIndex == "read_WU_device":
                            self.graphLines[key].appendDataPoint(int(data[number], 16))
                        else:
                            value = strToFloatElseNone(data[number])
                            if value is not None:
                                self.graphLines[key].appendDataPoint(value)
                    else:
                        print("not in range")
            else:
                if name[0] == kennung:
                    number = strToIntElseNone(name[1])
                    if number is not None:
                        if number >= 0 and number < len(data):
                            if serialParameters.readTextIndex == "read_WU_device":
                                self.graphLines[key].appendDataPoint(int(data[number], 16))
                            else:
                                value = strToFloatElseNone(data[number])
                                if value is not None:
                                    self.graphLines[key].appendDataPoint(value)
                        else:
                            print("not in range")



    def sendData(self):
        pass

    def save(self):
        return {"filterText": self.dataFilterLineEdit.text()}

    def load(self, data):
        self.dataFilterLineEdit.setText(data["filterText"])
