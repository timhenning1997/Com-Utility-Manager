from Window_Node_Editor.node_graphics_node import QDMGraphicsNode
from Window_Node_Editor.node_content_widget import QDMNodeContentWidget


class Node():
    def __init__(self, scene, hubWindow = None):
        self.scene = scene
        self.hubWindow = hubWindow
        self.locked = False

        self.initInnerClasses()

        self.locked = False

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

    def initInnerClasses(self):
        self.content = QDMNodeContentWidget()
        self.grNode = QDMGraphicsNode(self)

