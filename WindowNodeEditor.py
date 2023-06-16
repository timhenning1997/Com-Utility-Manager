from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters

from Window_Node_Editor.node_editor_wnd import NodeEditorWnd


class WindowNodeEditor(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "NodeEditor")
        self.resize(400, 400)

        mainWidget = NodeEditorWnd()
        self.setCentralWidget(mainWidget)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        pass #self.receiveDataLabel.setText(str(data))

    def sendData(self):
        # self.sendSerialData() ist eine interne Funktion, die die activen Ports berücksichtigt
        pass #self.sendSerialData("sending test data...")

    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        return None #self.receiveDataLabel.text()

    def load(self, data):
        pass #self.receiveDataLabel.setText(data)
