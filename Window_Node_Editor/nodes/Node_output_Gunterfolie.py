from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QTextEdit, QWidget, QSpinBox, QLabel
from Window_Node_Editor.node_node import Node
from Window_Node_Editor.node_content_widget import QDMNodeContentWidget
from Window_Node_Editor.node_graphics_node import QDMGraphicsNode
from Window_Node_Editor.select_measuring_points import SelectMeasuringPointsWindow

from SerialParameters import SerialParameters


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.label = QLabel()
        self.label.setFixedSize(50, 50)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)



class GraphicsNode(QDMGraphicsNode):
    def __init__(self, node, parent=None):
        super().__init__(node, parent)
        self.scale_item.hide()
        self.resize_item.hide()
        self.rotate_item.hide()
        self.filter_item.hide()
        self.option_item.hide()


class Node_GunterfolieOutputNode(Node):
    def __init__(self, scene: 'Scene', hubWindow = None):
        super().__init__(scene, hubWindow)
        self.grNode.changeContendSize(70, 70)

        self.index = 8

        self.minValue = 0
        self.maxValue = 65535

        self.color1 = QColor(0, 0, 0)
        self.color2 = QColor(255, 0, 0)

    def initInnerClasses(self):
        self.content = Content()
        self.grNode = GraphicsNode(self)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        if self.index < 0 or self.index >= len(data):
            return
        self.content.label.setText(str(int(data[self.index], 16)))
        number = int(data[self.index], 16)
        self.content.label.setStyleSheet("background-color: " + str(self.interpolateColor(self.color1, self.color2, (number - self.minValue) / (self.maxValue-self.minValue))) + ";")

    def interpolateColor(self, color1: QColor, color2: QColor, value: float) -> QColor:
        r = int(color1.red() + (color2.red() - color1.red()) * value)
        g = int(color1.green() + (color2.green() - color1.green()) * value)
        b = int(color1.blue() + (color2.blue() - color1.blue()) * value)
        return QColor(r, g, b).name()

