from PyQt5.QtWidgets import QMainWindow, QTableWidget, QVBoxLayout, QWidget, QTableWidgetItem


class SelectMeasuringPointsWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__()
        self.hubWindow = parent.node.hubWindow

        self.initUI()
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
        self.table.setHorizontalHeaderLabels(["BUTTON"] + tableHeadings)

        print(measuringPoints)

        for colIndex in range(0, len(measuringPoints)):
            for key in measuringPoints[colIndex].keys():
                value = measuringPoints[colIndex][key]
                rowIndex = tableHeadings.index(key) + 1
                tableWidget = QTableWidgetItem(value)
                self.table.setItem(colIndex, rowIndex, tableWidget)


        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.table)
        mainLayout.setContentsMargins(2, 2, 2, 2)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)
