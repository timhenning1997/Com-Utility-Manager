from Window_Node_Editor.node_graphics_scene import QDMGraphicsScene


class Scene():
    def __init__(self, parent=None):
        self.parent = parent
        self.nodes = []

        self.scene_width = 64000
        self.scene_height = 64000

        self.initUI()

    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    def addNode(self, node):
        self.nodes.append(node)

    def getView(self) -> 'QGraphicsView':
        return self.grScene.views()[0]

    def removeNode(self, node):
        self.nodes.remove(node)


