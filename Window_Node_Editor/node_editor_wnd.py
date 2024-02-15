from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from Window_Node_Editor.node_scene import Scene
from Window_Node_Editor.node_node import Node
from Window_Node_Editor.node_graphics_view import QDMGraphicsView
from Window_Node_Editor.nodes.Node_input_button import Node_TextButtonInputNode
from Window_Node_Editor.nodes.Node_output_Gunterfolie import Node_GunterfolieOutputNode


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
        X_pos = [61.05, 94.55, 128.05, 161.55, 195.05, 228.55, 262.05, 295.55, 329.05, 362.55, 396.05, 429.55, 463.05, 496.55, 530.05, 546.8, 77.8, 111.3, 144.8, 178.3, 195.05, 211.8, 245.3, 278.8, 312.3, 345.8, 412.8, 446.3, 463.05, 479.8, 513.3, 538.425, 61.05, 128.05, 161.55, 195.05, 211.8, 228.55, 262.05, 295.55, 329.05, 362.55, 379.3, 429.55, 463.05, 496.55, 530.05, 546.8, 61.05, 94.55, 111.3, 161.55, 195.05, 211.8, 245.3, 278.8, 312.3, 362.55, 396.05, 446.3, 446.3, 463.05, 513.3, 538.425, 61.05, 77.8, 102.925, 178.3, 195.05, 211.8, 228.55, 295.55, 345.8, 354.175, 412.8, 429.55, 446.3, 463.05, 479.8, 546.8, 61.05, 94.55, 102.925, 178.3, 195.05, 211.8, 228.55, 295.55, 312.3, 354.175, 412.8, 429.55, 446.3, 463.05, 479.8, 546.8, 77.8, 94.55, 111.3, 161.55, 195.05, 211.8, 245.3, 287.175, 329.05, 362.55, 396.05, 446.3, 463.05, 479.8, 496.55, 538.425, 61.05, 111.3, 136.425, 144.8, 178.3, 211.8, 245.3, 278.8, 312.3, 345.8, 379.3, 412.8, 446.3, 513.3, 521.675, 546.8]
        Y_pos = [257.63749, 257.65, 257.6375, 257.6375, 257.6375, 257.6375, 257.6375, 257.6375, 257.6375, 257.6375, 257.6375, 257.6375, 257.6375, 257.6375, 257.6375, 257.6375, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 243.36, 229.07, 229.07, 229.07, 229.07, 229.07, 229.07, 229.07, 229.07, 229.07, 243.36, 229.07, 229.07, 229.07, 229.07, 229.07, 236.21, 229.08, 214.79, 214.79, 214.79, 214.79, 214.79, 221.93, 221.93, 214.79, 229.07, 214.79, 229.07, 214.79, 221.93, 214.79, 221.93, 221.93, 200.51, 207.65, 200.51, 200.51, 207.65, 200.51, 214.79, 200.51, 214.79, 207.65, 200.51, 200.51, 214.79, 200.51, 171.94, 171.95, 186.23, 179.09, 186.23, 186.23, 179.09, 186.23, 171.94, 186.23, 171.94, 179.09, 186.23, 186.23, 179.09, 186.23, 164.80, 157.66, 171.94, 171.94, 171.94, 171.94, 171.94, 171.94, 164.80, 171.94, 164.80, 171.94, 171.94, 157.66, 164.80, 171.94, 157.6625, 157.6625, 164.8035, 157.6625, 157.6625, 157.6625, 157.6625, 157.6625, 157.6625, 157.6625, 157.6625, 157.6625, 157.6625, 157.6625, 164.8035, 157.6625]
        index = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128]
        minValue = 0
        maxValue = 65535

        for i in range(0, len(index)):
            node = Node_GunterfolieOutputNode(self.scene, self.hubWindow)
            node.index = index[i]
            node.minValue = minValue
            node.maxValue = maxValue
            node.grNode.setPos((X_pos[i]-61)*5, (Y_pos[i]-257)*5)
        # create graphics view
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

    def loadStylesheet(self, filename):
        print('STYLE loading:', filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))
