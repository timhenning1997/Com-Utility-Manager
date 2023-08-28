from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QTextEdit, QWidget
from Window_Node_Editor.node_node import Node
from Window_Node_Editor.node_content_widget import QDMNodeContentWidget
from Window_Node_Editor.node_graphics_node import QDMGraphicsNode
from Window_Node_Editor.select_measuring_points import SelectMeasuringPointsWindow

from SerialParameters import SerialParameters


class Content(QDMNodeContentWidget):
    def initUI(self):
        self.textEdit = QTextEdit("Send Signal")
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)



class GraphicsNode(QDMGraphicsNode):
    def __init__(self, node, parent=None):
        super().__init__(node, parent)

    def optionWindowPressed(self, x: int = 0, y: int = 0):
        self.window = SelectMeasuringPointsWindow(self)
        self.window.move(x - self.window.width() // 2, y - self.window.height() // 2)
        self.window.measurementPointsAddedSignal.connect(self.printSelectedMeasurementPoint)

    def printSelectedMeasurementPoint(self, uuid):
        print(uuid)


class Node_TextButtonInputNode(Node):
    def __init__(self, scene: 'Scene', hubWindow = None):
        super().__init__(scene, hubWindow)
        self.grNode.minWidth = 100
        self.grNode.minHeight = 50

    def initInnerClasses(self):
        self.content = Content()
        self.grNode = GraphicsNode(self)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        self.content.textEdit.setText(str(self.nodeEditorWindow.findCalibratedDataByUUID(data, dataInfo, "M1")))

