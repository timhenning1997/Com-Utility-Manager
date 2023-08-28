from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from Window_Node_Editor.node_scene import Scene
from Window_Node_Editor.node_node import Node
from Window_Node_Editor.node_graphics_view import QDMGraphicsView
from Window_Node_Editor.nodes.Node_input_button import Node_TextButtonInputNode


class NodeEditorWnd(QWidget):
    def __init__(self, parent=None, hubWindow=None):
        super().__init__(parent)

        self.parent = parent
        self.hubWindow = hubWindow

        self.stylesheet_filename = str(Path('qss/nodestyle.qss'))
        self.loadStylesheet(self.stylesheet_filename)

        self.initUI()


    def initUI(self):

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # crate graphics scene
        self.scene = Scene(self)
        # self.grScene = self.scene.grScene

        #node = Node(self.scene)
        node = Node_TextButtonInputNode(self.scene, self.hubWindow)

        # create graphics view
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

    def loadStylesheet(self, filename):
        print('STYLE loading:', filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))
