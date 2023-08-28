import math

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QTableWidget, QGridLayout, \
    QColorDialog, QTableWidgetItem, QComboBox
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters


class WindowTablePlotter(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "TablePlotter")
        self.resize(800, 400)

        self.receivedData = []
        self.receivedValueData = []
        self.currentLengthOfData = 0
        self.shownType = "Hex"

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

        self.shownTypeCB = QComboBox()
        self.shownTypeCB.addItem("Show: Hex")
        self.shownTypeCB.addItem("Show: Values")
        self.shownTypeCB.currentTextChanged.connect(self.changeShownType)

        colorOptionsLayout = QHBoxLayout()
        colorOptionsLayout.setContentsMargins(0, 0, 0, 0)
        colorOptionsLayout.setSpacing(1)
        colorOptionsLayout.addWidget(self.colorPicker1Button)
        colorOptionsLayout.addWidget(self.colorPicker2Button)
        colorOptionsLayout.addStretch()
        colorOptionsLayout.addWidget(self.shownTypeCB)

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
        if self.shownTypeCB.currentText() == "Show: Hex":
            self.shownType = "Hex"
        elif self.shownTypeCB.currentText() == "Show: Values":
            self.shownType = "Values"

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
                    if self.shownType == "Hex":
                        self.table.setItem(countY, countX, QTableWidgetItem(str(self.receivedData[1:][tableContendIndex])))
                    elif self.shownType == "Values":
                        self.table.setItem(countY, countX, QTableWidgetItem(str(self.receivedValueData[1:][tableContendIndex])))

                    number = int(self.receivedData[1:][tableContendIndex], 16)
                    self.table.item(countY, countX).setBackground(self.interpolateColor(self.color1, self.color2, number/65535))
                else:
                    self.table.setItem(countY, countX, QTableWidgetItem(""))
                self.table.item(countY, countX).setTextAlignment(Qt.AlignCenter)

    def interpolateColor(self, color1: QColor, color2: QColor, value: float) -> QColor:
        r = int(color1.red() + (color2.red() - color1.red()) * value)
        g = int(color1.green() + (color2.green() - color1.green()) * value)
        b = int(color1.blue() + (color2.blue() - color1.blue()) * value)
        return QColor(r, g, b)

    def addColumn(self):
        self.resizeTable(0, self.table.columnCount() + 1)

    def deleteLastColumn(self):
        if self.table.columnCount() > 1:
            self.resizeTable(0, self.table.columnCount() - 1)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        if serialParameters.readTextIndex == "read_WU_device" and dataInfo["dataType"] == "RAW-Values":
            self.receivedData = data

            self.receivedValueData = []
            for numberIndex in range(0, len(data)):
                self.receivedValueData.append(int(data[numberIndex], 16))

            if len(data[1:]) != self.currentLengthOfData:
                self.currentLengthOfData = len(data[1:])
                self.clearTable(len(data[1:]))
                if int(math.ceil(len(data[1:]) / self.colNumber)) != self.table.rowCount():
                    self.resizeTable(int(math.ceil(len(data[1:]) / self.colNumber)), self.colNumber)

            self.dataCounterLabel.setText(str(int(data[0], 16)))
            self.dataSetLengthLabel.setText(str(serialParameters.Kennung))
            self.errorCounterLabel.setText(str(serialParameters.errorCounter))

            temp_data = []
            temp_receivedValueData = []
            if len(data) > 1:
                temp_data = data[1:]
            if len(self.receivedValueData) > 1:
                temp_receivedValueData = self.receivedValueData[1:]

            for numberIndex in range(0, len(temp_data)):
                rowCount = numberIndex // self.colNumber
                colCount = numberIndex % self.colNumber

                if self.shownType == "Hex":
                    self.table.item(rowCount, colCount).setText(temp_data[numberIndex].upper())
                elif self.shownType == "Values":
                    self.table.item(rowCount, colCount).setText(str(temp_receivedValueData[numberIndex]))

                self.table.item(rowCount, colCount).setBackground(self.interpolateColor(self.color1, self.color2, temp_receivedValueData[numberIndex]/65535))

    def save(self):
        return {"rowCount": self.table.rowCount(),
                "colCount": self.table.columnCount(),
                "color1": self.color1.name(),
                "color2": self.color2.name()}

    def load(self, data):
        self.resizeTable(data["rowCount"], data["colCount"])
        self.color1.setNamedColor(data["color1"])
        self.colorPicker1Button.setStyleSheet("background-color : " + self.color1.name())
        self.color2.setNamedColor(data["color2"])
        self.colorPicker2Button.setStyleSheet("background-color : " + self.color2.name())
