import random

from PyQt5.QtCore import QPoint, Qt, QRunnable, pyqtSlot, QThreadPool, QProcess
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget, QLineEdit, QMenu, QGroupBox, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap, QFont
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters
from time import sleep


class WindowTest(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "Test")
        
        mainLayout = QHBoxLayout()
        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        pass

    def sendData(self):
        pass

    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        return ""

    def load(self, data):
        pass
