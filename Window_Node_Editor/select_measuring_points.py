from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QIcon
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QVBoxLayout, QWidget, QTableWidgetItem, QHeaderView, QPushButton, \
    QRadioButton


class SelectMeasuringPointsWindow(QMainWindow):
    measurementPointsAddedSignal = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__()
        self.hubWindow = parent.node.hubWindow

        self.initUI()
        self.resize(600, 600)
        self.show()

    def initUI(self):
        self.setWindowTitle("Select window")

        tableHeadings = []
        for file in self.hubWindow.measuringPointListFiles:
            for heading in file["HEADINGS"]:
                if heading not in tableHeadings:
                    tableHeadings.append(heading)

        measuringPoints = []
        for file in self.hubWindow.measuringPointListFiles:
            for index in range(len(file["DATA"]["UUID"])):
                if index is not None:
                    temp = {}
                    for key in file["DATA"].keys():
                        temp[key] = file["DATA"][key][index]
                    measuringPoints.append(temp)

        self.table = QTableWidget(len(measuringPoints), len(tableHeadings) + 1)
        self.table.setHorizontalHeaderLabels([""] + tableHeadings)

        plusIcon = QIcon("Window_Node_Editor/res/icons/circle_plus.ico")

        for colIndex in range(0, len(measuringPoints)):
            plusButton = QPushButton()
            plusButton.setProperty("colIndex", colIndex)
            if "UUID" in measuringPoints[colIndex].keys():
                plusButton.setProperty("UUID", measuringPoints[colIndex]["UUID"])
            plusButton.clicked.connect(self.addedButtonPressed)
            plusButton.setIcon(plusIcon)
            self.table.setCellWidget(colIndex, 0, plusButton)
            for key in measuringPoints[colIndex].keys():
                value = measuringPoints[colIndex][key]
                rowIndex = tableHeadings.index(key) + 1
                tableWidget = QTableWidgetItem(value)
                tableWidget.setFlags(Qt.ItemIsSelectable)
                self.table.setItem(colIndex, rowIndex, tableWidget)

        for i in range(0, self.table.columnCount()):
            self.table.resizeColumnToContents(i)
        self.table.setColumnWidth(0, 20)


        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.table)
        mainLayout.setContentsMargins(2, 2, 2, 2)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def addedButtonPressed(self):
        colIndex = self.sender().property("colIndex")
        uuid = self.sender().property("UUID")
        if uuid is not None:
            self.measurementPointsAddedSignal.emit(uuid)
        else:
            self.measurementPointsAddedSignal.emit(None)
        self.close()