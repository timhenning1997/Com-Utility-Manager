from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QTextEdit
from Window_Node_Editor.node_node import Node
from Window_Node_Editor.node_content_widget import QDMNodeContentWidget
from Window_Node_Editor.node_graphics_node import QDMGraphicsNode


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


class Node_TextButtonInputNode(Node):
    def __init__(self, scene: 'Scene'):
        super().__init__(scene)
        self.grNode.minWidth = 100
        self.grNode.minHeight = 50

    def initInnerClasses(self):
        self.content = Content()
        self.grNode = GraphicsNode(self)
