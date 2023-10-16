import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QFrame, QGroupBox, QWidget, QTableWidgetItem, \
    QTableWidget, QVBoxLayout, QScrollArea, QLabel


class MeasuringPointListWindow(QWidget):
    def __init__(self, path: str, measuringPointList):
        super().__init__()

        self.path = path
        self.measuringPointList = measuringPointList

        self.setWindowTitle("Measuring point list")

        self.measuringPointFiles = []

        for file in self.measuringPointList:
            if file["PATH"] == self.path:
                self.measuringPointFiles.append(file)

        tableHeadings = []
        for file in self.measuringPointFiles:
            for heading in file["HEADINGS"]:
                if heading not in tableHeadings:
                    tableHeadings.append(heading)

        measuringPoints = []
        for file in self.measuringPointFiles:
            for index in range(len(file["DATA"]["UUID"])):
                if index is not None:
                    temp = {}
                    for key in file["DATA"].keys():
                        temp[key] = file["DATA"][key][index]
                    measuringPoints.append(temp)

        self.table = QTableWidget(len(measuringPoints), len(tableHeadings))
        self.table.setHorizontalHeaderLabels(tableHeadings)

        for colIndex in range(0, len(measuringPoints)):
            for key in measuringPoints[colIndex].keys():
                value = measuringPoints[colIndex][key]
                rowIndex = tableHeadings.index(key)
                tableWidget = QTableWidgetItem(value)
                tableWidget.setFlags(Qt.ItemIsSelectable)
                self.table.setItem(colIndex, rowIndex, tableWidget)

        for i in range(0, self.table.columnCount()):
            self.table.resizeColumnToContents(i)

        # __________ Submit Button Layout __________
        self.cancelButton = QPushButton("Cancel")
        self.okButton = QPushButton("OK")
        self.okButton.setAutoDefault(True)

        submitButtonLayout = QHBoxLayout()
        submitButtonLayout.addStretch(1)
        submitButtonLayout.addWidget(self.okButton)
        submitButtonLayout.addWidget(self.cancelButton)

        # __________ Main Grid Layout __________
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.table)
        mainLayout.addLayout(submitButtonLayout)

        self.setLayout(mainLayout)

        # __________ QPushButton Function __________
        self.okButton.clicked.connect(self.close)
        self.cancelButton.clicked.connect(self.close)


class ScrollableLabelWindow(QScrollArea):
    def __init__(self, text: str = ""):
        QScrollArea.__init__(self)

        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        lay = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        lay.addWidget(self.label)
        self.label.setText(text)

    def setText(self, text: str = ""):
        self.label.setText(text)
