from PyQt5.QtWidgets import *


class QDMNodeContentWidget(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setMinimumSize(1, 1)

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.layout.addWidget(QTextEdit("foo"))
