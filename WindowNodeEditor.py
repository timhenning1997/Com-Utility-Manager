from PyQt5.QtWidgets import QLabel, QVBoxLayout, QPushButton, QWidget
from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters

from Window_Node_Editor.node_editor_wnd import NodeEditorWnd


class WindowNodeEditor(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "NodeEditor")
        self.resize(400, 400)

        self.mainWidget = NodeEditorWnd()
        self.setCentralWidget(self.mainWidget)

        self.sceneMousePosX = 0
        self.sceneMousePosY = 0
        self.sceneCenterPosX = 1
        self.sceneCenterPosY = 0
        self.sceneZoom = 0
        self.sceneFaktor = 1.25
        self.sceneScale = 100

        self.createStatusBar()

    def createStatusBar(self):
        self.statusBar().showMessage("")
        self.status_bar_label = QLabel("")
        self.statusBar().addPermanentWidget(self.status_bar_label)
        self.mainWidget.view.scenePosChanged.connect(self.onScenePosChanged)
        self.mainWidget.view.sceneScaleChanged.connect(self.onSceneScaleChanged)

    def onScenePosChanged(self, x:int, y:int):
        self.sceneMousePosX = x
        self.sceneMousePosY = y
        self.status_bar_label.setText("Zoom: [%d%%]  " % (self.sceneScale) + "Scene Pos: [%d, %d]" % (self.sceneMousePosX, self.sceneMousePosY))


    def onSceneScaleChanged(self, scale: float):
        self.sceneZoom = int(self.mainWidget.scene.getView().zoom - 20)
        self.sceneFaktor = self.mainWidget.scene.getView().zoomInFactor
        self.sceneScale = int(float(self.sceneFaktor)**self.sceneZoom * 100)
        self.status_bar_label.setText("Zoom: [%d%%]  " % (self.sceneScale) + "Scene Pos: [%d, %d]" % (self.sceneMousePosX, self.sceneMousePosY))

    def saveScenePosAndScale(self):
        sceneCenter = self.mainWidget.view.mapToScene(self.mainWidget.view.rect().center())
        self.sceneCenterPosX = sceneCenter.x()
        self.sceneCenterPosY = sceneCenter.y() + 11

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        pass #self.receiveDataLabel.setText(str(data))

    def sendData(self):
        # self.sendSerialData() ist eine interne Funktion, die die activen Ports berücksichtigt
        pass #self.sendSerialData("sending test data...")

    def save(self):
        # Mögliche Rückgabewerte sind String/Int/Float/List/Dict
        self.saveScenePosAndScale()
        return {
            "sceneCenterPosX": self.sceneCenterPosX,
            "sceneCenterPosY": self.sceneCenterPosY,
            "sceneZoom": self.sceneZoom + 20,
            "sceneFaktor": self.sceneFaktor
        }

    def load(self, data):
        self.mainWidget.scene.getView().zoom = data["sceneZoom"]
        self.mainWidget.scene.getView().zoomInFactor = data["sceneFaktor"]
        zoomFactor = data["sceneFaktor"]**(data["sceneZoom"]-20)
        self.mainWidget.view.scale(zoomFactor, zoomFactor)
        self.mainWidget.view.sceneScaleChanged.emit(float(zoomFactor))

        self.mainWidget.view.centerOn(data["sceneCenterPosX"], data["sceneCenterPosY"])

        self.saveScenePosAndScale()
