from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters


class WindowTest(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "Test")

        # Erstellung der GUI Oberfläche
        self.sendButton = QPushButton("Senden")
        self.sendButton.clicked.connect(self.sendData)
        self.receiveDataLabel = QLabel("receive Data")

        # Zuordnung der GUI Elemente in ein Layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.sendButton)
        mainLayout.addWidget(self.receiveDataLabel)

        # Dem Hauptfenster ein Layout zuweisen
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        self.receiveDataLabel.setText(str(data))

    def sendData(self):
        # self.sendSerialData() ist eine interne Funktion, die die activen Ports berücksichtigt
        self.sendSerialData("sending test data...")

    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        return self.receiveDataLabel.text()

    def load(self, data):
        self.receiveDataLabel.setText(data)
