from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters


class WindowTest(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "Test")

        # Erstellung der GUI Oberfläche
        self.sendButton = QPushButton("Senden")
        self.sendButton.clicked.connect(self.sendData)
        self.receiveDataLabel = QLabel("receive Data")
        self.receiveDataLabel.setMaximumWidth(200)

        # Test
        self.auswahlLineEdit = QLineEdit()
        self.indexLabel = QLabel("Index: ")
        self.auswahlLabel = QLabel("Value: ")

        # Zuordnung der GUI Elemente in ein Layout
        mainLayout = QVBoxLayout()
        #mainLayout.addWidget(self.sendButton)
        #mainLayout.addWidget(self.receiveDataLabel)

        # Test
        mainLayout.addWidget(self.auswahlLineEdit)
        mainLayout.addWidget(self.indexLabel)
        mainLayout.addWidget(self.auswahlLabel)

        # Dem Hauptfenster ein Layout zuweisen
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        self.receiveDataLabel.setText(str(data) + " | INFO: " + str(dataInfo))
        self.indexLabel.setText("Index: " + str(self.findIndexByUUID(data, dataInfo, self.auswahlLineEdit.text())))
        self.auswahlLabel.setText("Value: " + str(self.findCalibratedDataByUUID(data, dataInfo, self.auswahlLineEdit.text())))

        print(self.findCalibratedDataByKeyValue(data, dataInfo, "Messstelle", "TA2"))

    def sendData(self):
        # self.sendSerialData() ist eine interne Funktion, die die activen Ports berücksichtigt
        self.sendSerialData("sending test data...")

    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        return self.receiveDataLabel.text()

    def load(self, data):
        self.receiveDataLabel.setText(data)
