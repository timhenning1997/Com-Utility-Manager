import binascii
import math
import bisect

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QTableWidget, QGridLayout, \
    QColorDialog, QTableWidgetItem, QComboBox, QSpinBox
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters

class MySpinBox(QSpinBox):

    def __init__(self):
        super().__init__()
        self.lineEdit().setVisible(False)
        self.setFixedWidth(30)
    def focusInEvent(self, event):
        self.setFixedWidth(150)
        self.lineEdit().setVisible(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setFixedWidth(30)
        self.lineEdit().setVisible(False)
        super().focusOutEvent(event)



class WindowTablePlotter(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "TablePlotter")
        self.resize(800, 400)

        self.receivedData = []
        self.receivedValueData = []
        self.receivedMaxMinData = []
        self.savedMaxMinData = {}
        self.currentLengthOfData = 0
        self.shownType = "Hex"
        self.minValue = 0
        self.maxValue = 65535

        self.color1 = QColor(26, 26, 26)
        self.color2 = QColor(77, 0, 0)

        colorScalaLabel = QLabel("Color scala ")

        self.colorPicker1Button = QPushButton("")
        self.colorPicker1Button.setFixedWidth(20)
        self.colorPicker1Button.setStyleSheet("background-color : " + self.color1.name())
        self.colorPicker1Button.clicked.connect(self.colorPicker1)
        self.colorPicker1Button.setContentsMargins(0, 0, 0, 0)
        self.colorPicker2Button = QPushButton("")
        self.colorPicker2Button.setFixedWidth(20)
        self.colorPicker2Button.setStyleSheet("background-color : " + self.color2.name())
        self.colorPicker2Button.clicked.connect(self.colorPicker2)
        self.colorPicker2Button.setContentsMargins(0, 0, 0, 0)

        separatorLabel = QLabel("|")
        self.minValueSpinBox = MySpinBox()
        self.minValueSpinBox.setRange(-999999, 999999)
        self.minValueSpinBox.setValue(0)
        self.minValueSpinBox.setPrefix("min: ")
        self.minValueSpinBox.valueChanged.connect(self.changeMinMaxValues)
        self.maxValueSpinBox = MySpinBox()
        self.maxValueSpinBox.setRange(-999999, 999999)
        self.maxValueSpinBox.setValue(65535)
        self.maxValueSpinBox.setPrefix("max: ")
        self.maxValueSpinBox.valueChanged.connect(self.changeMinMaxValues)

        self.shownTypeCB = QComboBox()
        self.shownTypeCB.addItem("Show: Hex")
        self.shownTypeCB.addItem("Show: Values")
        self.shownTypeCB.addItem("Show: Max-Min")
        self.shownTypeCB.addItem("Show: Cal")
        self.shownTypeCB.currentTextChanged.connect(self.changeShownType)

        self.maxMinDataPointsSpinBox = QSpinBox()
        self.maxMinDataPointsSpinBox.setPrefix("of last: ")
        self.maxMinDataPointsSpinBox.setSuffix(" Data points")
        self.maxMinDataPointsSpinBox.setRange(2, 1000)
        self.maxMinDataPointsSpinBox.setValue(5)
        self.maxMinDataPointsSpinBox.hide()

        colorOptionsLayout = QHBoxLayout()
        colorOptionsLayout.setContentsMargins(0, 0, 0, 0)
        colorOptionsLayout.setSpacing(1)
        colorOptionsLayout.addWidget(self.minValueSpinBox)
        colorOptionsLayout.addWidget(self.colorPicker1Button)
        colorOptionsLayout.addWidget(separatorLabel)
        colorOptionsLayout.addWidget(self.maxValueSpinBox)
        colorOptionsLayout.addWidget(self.colorPicker2Button)
        colorOptionsLayout.addStretch()
        colorOptionsLayout.addWidget(self.shownTypeCB)
        colorOptionsLayout.addWidget(self.maxMinDataPointsSpinBox)

        addColumnButton = QPushButton("+ Column")
        addColumnButton.clicked.connect(self.addColumn)
        deleteColumnButton = QPushButton("- Column")
        deleteColumnButton.clicked.connect(self.deleteLastColumn)

        optionsLayout = QHBoxLayout()
        optionsLayout.addWidget(colorScalaLabel)
        optionsLayout.addLayout(colorOptionsLayout)
        optionsLayout.addStretch()
        optionsLayout.addWidget(deleteColumnButton)
        optionsLayout.addWidget(addColumnButton)

        dataCounterTextLabel = QLabel("Data couter:")
        dataCounterTextLabel.adjustSize()
        self.dataCounterLabel = QLabel("Data couter")
        self.dataCounterLabel.setFixedWidth(50)
        dataSetLengthTextLabel = QLabel("NDL:")
        dataSetLengthTextLabel.adjustSize()
        self.dataSetLengthLabel = QLabel("NDL")
        self.dataSetLengthLabel.setFixedWidth(50)
        errorCounterTextLabel = QLabel("Error counter:")
        errorCounterTextLabel.adjustSize()
        self.errorCounterLabel = QLabel("0")
        self.errorCounterLabel.setFixedWidth(50)

        options2Layout = QHBoxLayout()
        options2Layout.addWidget(dataCounterTextLabel)
        options2Layout.addWidget(self.dataCounterLabel)
        options2Layout.addWidget(dataSetLengthTextLabel)
        options2Layout.addWidget(self.dataSetLengthLabel)
        options2Layout.addWidget(errorCounterTextLabel)
        options2Layout.addWidget(self.errorCounterLabel)
        options2Layout.addStretch()

        self.colNumber = 8
        self.table = QTableWidget(0, 0)
        self.resizeTable(0, self.colNumber)



        mainLayout = QVBoxLayout()
        mainLayout.addLayout(optionsLayout)
        mainLayout.addLayout(options2Layout)
        mainLayout.addWidget(self.table)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def colorPicker1(self):
        color = QColorDialog.getColor().name()
        self.colorPicker1Button.setStyleSheet("background-color : " + color)
        self.color1 = QColor(color)

    def colorPicker2(self):
        color = QColorDialog.getColor().name()
        self.colorPicker2Button.setStyleSheet("background-color : " + color)
        self.color2 = QColor(color)

    def changeShownType(self):
        self.maxMinDataPointsSpinBox.hide()
        if self.shownTypeCB.currentText() == "Show: Hex":
            self.shownType = "Hex"
        elif self.shownTypeCB.currentText() == "Show: Values":
            self.shownType = "Values"
        elif self.shownTypeCB.currentText() == "Show: Max-Min":
            self.shownType = "MaxMin"
            self.savedMaxMinData.clear()
            self.maxMinDataPointsSpinBox.show()
        elif self.shownTypeCB.currentText() == "Show: Cal":
            self.shownType = "Cal"

    def clearTable(self, dataLength: int = 0):
        counter = 0
        for countY in range(0, self.table.rowCount()):
            for countX in range(0, self.table.columnCount()):
                self.table.item(countY, countX).setBackground(QColor(Qt.transparent))
                if counter >= dataLength:
                    self.table.item(countY, countX).setText("")
                counter += 1

    def changeTableSize(self, rowCount: int, columnCount: int):
        self.table.setRowCount(rowCount)
        self.table.setColumnCount(columnCount)

    def changeTableHeaderLabels(self):
        verticalHeaderLabels = []
        for count in range(0, self.table.rowCount()):
            verticalHeaderLabels.append("AN " + str(count))
        self.table.setVerticalHeaderLabels(verticalHeaderLabels)
        horizontalHeaderLabels = []
        for count in range(0, self.table.columnCount()):
            horizontalHeaderLabels.append("CH " + str(count))
        self.table.setHorizontalHeaderLabels(horizontalHeaderLabels)

    def changeTableColumnWidth(self, width):
        for count in range(0, self.table.columnCount()):
            self.table.setColumnWidth(count, width)

    def changeMinMaxValues(self):
        self.minValue = self.minValueSpinBox.value()
        self.maxValue = self.maxValueSpinBox.value()

    def focusInMinMaxValues(self):
        self.minValueSpinBox.adjustSize()
        self.maxValueSpinBox.adjustSize()

    def focusOutMinMaxValues(self):
        self.minValueSpinBox.setFixedWidth(30)
        self.maxValueSpinBox.setFixedWidth(30)

    def resizeTable(self, rowCount: int, columnCount: int):
        if rowCount == 0:
            rowCount = int(math.ceil(len(self.receivedData[1:]) / columnCount))

        self.colNumber = columnCount
        self.changeTableSize(rowCount, columnCount)
        self.changeTableHeaderLabels()
        self.changeTableColumnWidth(90)


        for countY in range(0, self.table.rowCount()):
            for countX in range(0, self.table.columnCount()):
                tableContendIndex = countY * (self.table.columnCount()) + countX
                if len(self.receivedData[1:]) > tableContendIndex:
                    if type(self.receivedData[1:][tableContendIndex]) in [int, float]:
                        number = self.receivedData[1:][tableContendIndex]
                    else:
                        number = int(self.receivedData[1:][tableContendIndex], 16)
                    if self.shownType == "Hex":
                        self.table.setItem(countY, countX, QTableWidgetItem(str(number)))
                        self.table.item(countY, countX).setBackground(self.interpolateColor(self.color1, self.color2, (number - self.minValue) / (self.maxValue-self.minValue)))
                    elif self.shownType == "Values":
                        self.table.setItem(countY, countX, QTableWidgetItem(str(self.receivedValueData[1:][tableContendIndex])))
                        self.table.item(countY, countX).setBackground(self.interpolateColor(self.color1, self.color2, (number - self.minValue) / (self.maxValue-self.minValue)))
                    elif self.shownType == "MaxMin":
                        self.table.setItem(countY, countX, QTableWidgetItem(str(self.receivedMaxMinData[1:][tableContendIndex])))
                        self.table.item(countY, countX).setBackground(QColor(Qt.transparent))
                    elif self.shownType == "Cal":
                        self.table.setItem(countY, countX, QTableWidgetItem(str(self.receivedValueData[1:][tableContendIndex])))
                        self.table.item(countY, countX).setBackground(QColor(Qt.transparent))
                else:
                    self.table.setItem(countY, countX, QTableWidgetItem(""))
                self.table.item(countY, countX).setTextAlignment(Qt.AlignCenter)

    def interpolateColor(self, color1: QColor, color2: QColor, value: float) -> QColor:
        r = int(color1.red() + (color2.red() - color1.red()) * value)
        g = int(color1.green() + (color2.green() - color1.green()) * value)
        b = int(color1.blue() + (color2.blue() - color1.blue()) * value)
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return QColor(r, g, b)

    def addColumn(self):
        self.resizeTable(0, self.table.columnCount() + 1)

    def deleteLastColumn(self):
        if self.table.columnCount() > 1:
            self.resizeTable(0, self.table.columnCount() - 1)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        uuidData, limitColorsData = None, None
        if serialParameters.readTextIndex == "read_WU_device" and dataInfo["dataType"] == "CALIBRATED-Values":
            if "LIMIT_COLOR_DATA" in data.keys():
                uuidData = data["UUID"]
                uuidData.append("#LastUUIDNotUsed#") # Ersetzt die UUID für "4f4b == "OK" Ausgabe in den Kalibrierten Daten von Bennies Programm"
                limitColorsData = data["LIMIT_COLOR_DATA"]
            data = data["DATA"]
            data.append(0) # Ersetzt die "4f4b == "OK" Ausgabe in den Kalibrierten Daten von Bennies Programm"

        if serialParameters.readTextIndex == "read_WU_device": # and dataInfo["dataType"] == "RAW-Values":
            self.receivedData = data

            self.receivedValueData = []
            if dataInfo["dataType"] == "RAW-Values":
                for numberIndex in range(0, len(data)):
                    self.receivedValueData.append(int(data[numberIndex], 16))
            elif dataInfo["dataType"] == "CALIBRATED-Values":
                self.receivedValueData = data

            kennung = binascii.hexlify(serialParameters.Kennbin).decode("utf-8").upper()
            self.receivedMaxMinData = []
            if self.shownType == "MaxMin" and dataInfo["dataType"] == "RAW-Values":
                if kennung not in self.savedMaxMinData.keys():
                    self.savedMaxMinData[kennung] = []
                    for numberIndex in range(0, len(self.receivedValueData)):
                        self.savedMaxMinData[kennung].append([self.receivedValueData[numberIndex]])
                        self.receivedMaxMinData.append(self.receivedValueData[numberIndex])
                else:
                    for numberIndex in range(0, len(self.receivedValueData)):
                        self.savedMaxMinData[kennung][numberIndex].append(self.receivedValueData[numberIndex])
                        self.savedMaxMinData[kennung][numberIndex] = self.savedMaxMinData[kennung][numberIndex][-self.maxMinDataPointsSpinBox.value():]
                        self.receivedMaxMinData.append(max(self.savedMaxMinData[kennung][numberIndex])-min(self.savedMaxMinData[kennung][numberIndex]))

            if len(self.receivedValueData[1:]) != self.currentLengthOfData:
                self.currentLengthOfData = len(self.receivedValueData[1:])
                self.clearTable(len(self.receivedValueData[1:]))
                if int(math.ceil(len(self.receivedValueData[1:]) / self.colNumber)) != self.table.rowCount():
                    self.resizeTable(int(math.ceil(len(self.receivedValueData[1:]) / self.colNumber)), self.colNumber)

            self.dataCounterLabel.setText(str(self.receivedValueData[0]))
            self.dataSetLengthLabel.setText(str(serialParameters.Kennung))
            self.errorCounterLabel.setText(str(serialParameters.errorCounter))

            temp_data = []
            temp_receivedValueData = []
            temp_receivedMaxMinData = []
            if len(self.receivedValueData) > 1:
                temp_data = [str(x) for x in data[1:]]
            if len(self.receivedValueData) > 1:
                temp_receivedValueData = self.receivedValueData[1:]
            if len(self.receivedMaxMinData) > 1:
                temp_receivedMaxMinData = self.receivedMaxMinData[1:]

            for numberIndex in range(0, len(temp_data)):
                rowCount = numberIndex // self.colNumber
                colCount = numberIndex % self.colNumber

                if dataInfo["dataType"] == "RAW-Values" and self.shownType == "Hex" and len(temp_data) > 0:
                    self.table.item(rowCount, colCount).setText(temp_data[numberIndex].upper())
                    self.table.item(rowCount, colCount).setBackground(self.interpolateColor(self.color1, self.color2, (temp_receivedValueData[numberIndex]-self.minValue) / (self.maxValue-self.minValue)))
                elif dataInfo["dataType"] == "RAW-Values" and self.shownType == "Values" and len(temp_receivedValueData) > 0:
                    self.table.item(rowCount, colCount).setText(str(temp_receivedValueData[numberIndex]))
                    self.table.item(rowCount, colCount).setBackground(self.interpolateColor(self.color1, self.color2, (temp_receivedValueData[numberIndex]-self.minValue) / (self.maxValue-self.minValue)))
                elif dataInfo["dataType"] == "RAW-Values" and self.shownType == "MaxMin" and len(temp_receivedMaxMinData) > 0:
                    self.table.item(rowCount, colCount).setText(str(temp_receivedMaxMinData[numberIndex]))
                    #self.table.item(rowCount, colCount).setBackground(QColor(Qt.transparent))
                    self.table.item(rowCount, colCount).setBackground(self.interpolateColor(self.color1, self.color2, (temp_receivedMaxMinData[numberIndex] - self.minValue) / (self.maxValue - self.minValue)))
                elif dataInfo["dataType"] == "CALIBRATED-Values" and self.shownType == "Cal" and len(temp_receivedValueData) > 0:
                    color = "transparent"
                    if uuidData is not None:
                        for limitColorData in limitColorsData:
                            if uuidData[numberIndex+1] == limitColorData["UUID"]:
                                colorIndex = bisect.bisect_right(limitColorData["limits"], temp_receivedValueData[numberIndex])
                                color = limitColorData["colors"][colorIndex]
                    self.table.item(rowCount, colCount).setText(str(temp_receivedValueData[numberIndex]))
                    self.table.item(rowCount, colCount).setBackground(QColor(color))

    def save(self):
            return {"rowCount": self.table.rowCount(),
                    "colCount": self.table.columnCount(),
                    "color1": self.color1.name(),
                    "color2": self.color2.name(),
                    "minValue": self.minValue,
                    "maxValue": self.maxValue,
                    "shownTypeCB": self.shownTypeCB.currentText()}

    def load(self, data):
        self.resizeTable(data["rowCount"], data["colCount"])
        self.color1.setNamedColor(data["color1"])
        self.colorPicker1Button.setStyleSheet("background-color : " + self.color1.name())
        self.color2.setNamedColor(data["color2"])
        self.colorPicker2Button.setStyleSheet("background-color : " + self.color2.name())
        self.minValue = data["minValue"]
        self.minValueSpinBox.setValue(data["minValue"])
        self.maxValue = data["maxValue"]
        self.maxValueSpinBox.setValue(data["maxValue"])
        self.shownTypeCB.setCurrentText(data["shownTypeCB"])
