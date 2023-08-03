from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters


class GraphicalMeasurement(QWidget):
    def __init__(self, parent, x: int, y: int, uuid: str, name: str = "NAME", unit: str = ""):
        super().__init__(parent)

        self.move(x, y)
        self.setFixedSize(100, 55)
        self.setContentsMargins(0, 0, 0, 0)

        self.uuid = uuid
        self.name = name
        self.unit = unit

        groupbox = QGroupBox()
        groupbox.setStyleSheet("QGroupBox {background-color: green;}")
        groupbox.setContentsMargins(0, 0, 0, 0)
        groupbox.setFixedSize(90, 45)

        layout = QVBoxLayout()
        layout.addWidget(groupbox)

        self.nameLabel = QLabel(self.name, groupbox)
        self.nameLabel.move(5, 0)
        self.nameLabel.setFixedSize(50, 20)

        self.valueLabel = QLabel("Value", groupbox)
        self.valueLabel.move(5, 25)
        self.valueLabel.setFixedSize(50, 20)

        self.unitLabel = QLabel(self.unit, groupbox)
        self.unitLabel.move(60, 25)
        self.unitLabel.setFixedSize(50, 20)

        self.setLayout(layout)

    def setValueText(self, value: str):
        self.valueLabel.setText(value)

class WindowTest(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "Test")

        # Erstellung der GUI Oberfläche
        #self.sendButton = QPushButton("Senden")
        #self.sendButton.clicked.connect(self.sendData)
        #self.receiveDataLabel = QLabel("receive Data")
        #self.receiveDataLabel.setMaximumWidth(200)

        # Test
        #self.auswahlLineEdit = QLineEdit()
        #self.indexLabel = QLabel("Index: ")
        #self.auswahlLabel = QLabel("Value: ")

        # Zuordnung der GUI Elemente in ein Layout
        #mainLayout = QVBoxLayout()
        #mainLayout.addWidget(self.sendButton)
        #mainLayout.addWidget(self.receiveDataLabel)

        # Test
        #mainLayout.addWidget(self.auswahlLineEdit)
        #mainLayout.addWidget(self.indexLabel)
        #mainLayout.addWidget(self.auswahlLabel)

        # Dem Hauptfenster ein Layout zuweisen
        mainLayout = QVBoxLayout()
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        # Test 2
        self.graphicalMeasurements = []
        self.graphicalMeasurements.append(GraphicalMeasurement(mainWidget, 40, 20, "GeraetXY_Messstelle_Z0", "TestName", "mm"))
        self.graphicalMeasurements.append(GraphicalMeasurement(mainWidget, 50, 50, "TestUUID2", "Tesame2", "mm2"))



    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        #self.receiveDataLabel.setText(str(data) + " | INFO: " + str(dataInfo))
        #self.indexLabel.setText("Index: " + str(self.findIndexByUUID(data, dataInfo, self.auswahlLineEdit.text())))
        #self.indexLabel.setText(str(self.findCalibratedDataByKeyValue(data, dataInfo, "Messstelle", self.auswahlLineEdit.text())))

        for graphicalMeasurement in self.graphicalMeasurements:
            graphicalMeasurement.setValueText(str(self.findCalibratedDataByUUID(data, dataInfo, graphicalMeasurement.uuid)))

    def sendData(self):
        # self.sendSerialData() ist eine interne Funktion, die die activen Ports berücksichtigt
        self.sendSerialData("sending test data...")

    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        return ""

    def load(self, data):
        pass

    def contextMenuEvent(self, event):

        context_menu = QMenu()

        listDatas = self._hubWindow.measuringPointListFiles
        for listData in listDatas:
            for key in listData["DATA"].keys():
                subMenu = QMenu(str(key), self)
                for value in listData["DATA"][key]:
                    subAction = subMenu.addAction(str(value))
                    subAction.setProperty("key", key)
                    subAction.setProperty("value", value)
                context_menu.addMenu(subMenu)

        action = context_menu.exec_(QPoint(0, 0))
        print("key: ", action.property("key"), "  value: ", action.property("value"))
