import math

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *



class QDMGraphicsNode(QGraphicsItem):
    def __init__(self, node, parent: QWidget = None):
        super().__init__(parent)
        self.node = node
        self.content = self.node.content
        self.setAcceptHoverEvents(True)


        self.width = 180
        self.height = 240
        self.minWidth = 1
        self.minHeight = 1
        self.edge_size = 10

        self.hovered = False

        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))
        self._pen_hovered = QPen(QColor("#FF37A6FF"))
        self._pen_hovered.setWidthF(3.0)

        self._brush_background = QBrush(QColor("#E3212121"))

        # init content
        self.initContent()

        self.initAssets()
        self.initUI()
        self.initIcons()


    def boundingRect(self):
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.hovered = False
        self.update()

    def initAssets(self):
        self.scaleIcon = QImage("Window_Node_Editor/res/icons/scale_icon.png")
        self.resizeIcon = QImage("Window_Node_Editor/res/icons/resize_icon.png")
        self.rotateIcon = QImage("Window_Node_Editor/res/icons/rotate_icon.png")
        self.filterIcon = QImage("Window_Node_Editor/res/icons/filter_icon.png")
        self.optionIcon = QImage("Window_Node_Editor/res/icons/option2_icon.png")

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def initIcons(self):
        self.scale_item = ScaleIconItem(self, self.scaleIcon)
        self.scale_item.setPos(self.width - 18, self.height + 2)
        self.scale_item.setEnabled(True)
        self.scale_item.show()

        self.resize_item = ResizeIconItem(self, self.resizeIcon)
        self.resize_item.setPos(self.width - 38, self.height + 2)
        self.resize_item.setEnabled(True)
        self.resize_item.show()

        self.rotate_item = RotateIconItem(self, self.rotateIcon)
        self.rotate_item.setPos(self.width + 2, self.height + 2)
        self.rotate_item.setEnabled(True)
        self.rotate_item.show()

        self.filter_item = FilterIconItem(self, self.filterIcon)
        self.filter_item.setPos(0, -17)
        self.filter_item.setEnabled(True)
        self.filter_item.show()

        self.option_item = OptionIconItem(self, self.optionIcon)
        self.option_item.setPos(self.width + 2, -17)
        self.option_item.setEnabled(True)
        self.option_item.show()

    def initContent(self):
        self.grContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.edge_size, self.edge_size, self.width - 2*self.edge_size, self.height - 2*self.edge_size)
        self.grContent.setWidget(self.content)

    def changeContendSize(self, width=-1, height=-1):
        if self.content is None:
            return
        if width < self.minWidth: width = self.minWidth
        if height < self.minHeight: height = self.minHeight
        if width > 0 and height > 0:
            self.width = width
            self.height = height

        self.content.setGeometry(self.edge_size, self.edge_size, self.width - 2 * self.edge_size,
                                 self.height - 2 * self.edge_size)

        self.scale_item.setPos(self.width - 18, self.height + 2)
        self.resize_item.setPos(self.width - 38, self.height + 2)
        self.rotate_item.setPos(self.width + 2, self.height + 2)
        self.filter_item.setPos(0, -17)
        self.option_item.setPos(self.width + 2, -17)

    def filterWindowPressed(self, x: int = 0, y: int = 0):
        print("X: ", x, "   Y: ", y)

    def optionWindowPressed(self, x: int = 0, y: int = 0):
        print("X: ", x, "   Y: ", y)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())


        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setBrush(Qt.NoBrush)
        if self.hovered and not self.node.locked:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())

        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())


class ScaleIconItem(QGraphicsItem):
    def __init__(self, parent, imageObj):
        super().__init__(parent)
        self.grNode = parent
        self.imageObj = imageObj
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent, False)
        self.startMousePos = QPointF(0.0, 0.0)

    def contextMenuEvent(self, event):
        if self.grNode.node.locked:
            return

        context_menu = QMenu()
        for i in range(1, 6):
            changeAct = context_menu.addAction(str(i*20) + "%")
            changeAct.setProperty("actionType", "change")
            changeAct.setProperty("scale", i*20)
        for i in range(1, 6):
            changeAct = context_menu.addAction(str(i*200) + "%")
            changeAct.setProperty("actionType", "change")
            changeAct.setProperty("scale", i*200)

        view = self.grNode.node.scene.getView()

        zoom = int(self.grNode.node.scene.getView().zoom - self.grNode.node.scene.getView().startZoom)
        faktor = self.grNode.node.scene.getView().zoomInFactor
        zoomFaktor = float(faktor) ** zoom
        scaleFaktor = self.grNode.scale()

        viewPos = view.mapToGlobal(QPoint(0, 0))
        grNodePos = view.mapFromScene(self.grNode.pos().x(), self.grNode.pos().y())
        angle = self.grNode.rotation()
        newX = (event.pos().x() + self.pos().x()) * math.cos(math.radians(angle)) - \
               (event.pos().y() + self.pos().y()) * math.sin(math.radians(angle))
        newY = (event.pos().x() + self.pos().x()) * math.sin(math.radians(angle)) + \
               (event.pos().y() + self.pos().y()) * math.cos(math.radians(angle))
        eventPos = QPoint(int(newX * zoomFaktor * scaleFaktor),
                          int(newY * zoomFaktor * scaleFaktor))
        action = context_menu.exec_(viewPos + grNodePos + eventPos)

        if action and action.property("actionType"):
            if action.property("actionType") == "change":
                scale = action.property("scale")
                self.grNode.setScale(scale/100)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.startMousePos = event.pos()

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        if self.grNode.node.locked:
            return
        width = self.grNode.width
        mousePosX = event.pos().x() - self.startMousePos.x()
        grNodeScale = self.grNode.scale()
        newScale = grNodeScale * (1 + mousePosX / width)
        self.grNode.setScale(newScale)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        super().mouseReleaseEvent(event)


    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if self.grNode.node.locked:
            return
        painter.drawImage(QRectF(0, 0, 20, 15), self.imageObj, QRectF(0, 0, 40.0, 30.0))

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 20, 15).normalized()


class ResizeIconItem(QGraphicsItem):
    def __init__(self, parent, imageObj):
        super().__init__(parent)
        self.grNode = parent
        self.imageObj = imageObj
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent, False)
        self.startMousePos = QPointF(0.0, 0.0)
        self.startGrNodeWidth = self.grNode.width
        self.startGrNodeHeight = self.grNode.height

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.startMousePos = self.mapToParent(event.pos())
        self.startGrNodeWidth = self.grNode.width
        self.startGrNodeHeight = self.grNode.height

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        if self.grNode.node.locked:
            return
        mousePos = self.mapToParent(event.pos()) - self.startMousePos
        self.grNode.changeContendSize(int(self.startGrNodeWidth + mousePos.x()), int(self.startGrNodeHeight + mousePos.y()))

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        super().mouseReleaseEvent(event)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if self.grNode.node.locked:
            return
        painter.drawImage(QRectF(0, 0, 20, 15), self.imageObj, QRectF(0, 0, 40.0, 30.0))

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 20, 15).normalized()


class RotateIconItem(QGraphicsItem):
    def __init__(self, parent, imageObj):
        super().__init__(parent)
        self.grNode = parent
        self.imageObj = imageObj
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent, False)

    def contextMenuEvent(self, event):
        if self.grNode.node.locked:
            return

        context_menu = QMenu()
        for i in range(0, 8):
            changeAct = context_menu.addAction(str(i*45) + "°")
            changeAct.setProperty("actionType", "change")
            changeAct.setProperty("angle", i*45)

        view = self.grNode.node.scene.getView()

        zoom = int(self.grNode.node.scene.getView().zoom - self.grNode.node.scene.getView().startZoom)
        faktor = self.grNode.node.scene.getView().zoomInFactor
        zoomFaktor = float(faktor) ** zoom
        scaleFaktor = self.grNode.scale()

        viewPos = view.mapToGlobal(QPoint(0, 0))
        grNodePos = view.mapFromScene(self.grNode.pos().x(), self.grNode.pos().y())
        angle = self.grNode.rotation()
        newX = (event.pos().x() + self.pos().x()) * math.cos(math.radians(angle)) - \
               (event.pos().y() + self.pos().y()) * math.sin(math.radians(angle))
        newY = (event.pos().x() + self.pos().x()) * math.sin(math.radians(angle)) + \
               (event.pos().y() + self.pos().y()) * math.cos(math.radians(angle))
        eventPos = QPoint(int(newX * zoomFaktor * scaleFaktor),
                          int(newY * zoomFaktor * scaleFaktor))
        action = context_menu.exec_(viewPos + grNodePos + eventPos)

        if action and action.property("actionType"):
            if action.property("actionType") == "change":
                angle = action.property("angle")
                self.globalRotationPoint = self.grNode.mapToParent(QPointF(self.grNode.width / 2, self.grNode.height / 2))
                newPos = self.getPosFromRotation(self.grNode.pos().x(), self.grNode.pos().y(), angle - self.grNode.rotation(),
                                                 self.globalRotationPoint.x(), self.globalRotationPoint.y())
                self.grNode.setRotation(angle)
                self.grNode.setPos(newPos.x(), newPos.y())


    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        self.grNodeStartRot = self.grNode.rotation()
        self.grNodeStartPos = self.grNode.pos()
        self.globalRotationPoint = self.grNode.mapToParent(QPointF(self.grNode.width / 2, self.grNode.height / 2))
        self.startMousePos = self.grNode.mapToParent(self.mapToParent(event.pos()))

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        if self.grNode.node.locked:
            return
        mousePos = self.grNode.mapToParent(self.mapToParent(event.pos()))
        angle = self.getAngle(self.startMousePos, self.globalRotationPoint, mousePos)
        newPos = self.getPosFromRotation(self.grNodeStartPos.x(), self.grNodeStartPos.y(), angle,
                                         self.globalRotationPoint.x(), self.globalRotationPoint.y())
        self.grNode.setRotation(angle + self.grNodeStartRot)
        self.grNode.setPos(newPos.x(), newPos.y())

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'):
        super().mouseReleaseEvent(event)

    def getPosFromRotation(self, x, y, angle, xOld=0, yOld=0):
        newX = (x-xOld) * math.cos(math.radians(angle)) - (y-yOld) * math.sin(math.radians(angle)) + xOld
        newY = (x-xOld) * math.sin(math.radians(angle)) + (y-yOld) * math.cos(math.radians(angle)) + yOld
        return QPointF(newX, newY)

    def getAngle(self, a, b, c):
        ang = math.degrees(math.atan2(c.y() - b.y(), c.x() - b.x()) - math.atan2(a.y() - b.y(), a.x() - b.x()))
        return ang

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if self.grNode.node.locked:
            return
        painter.drawImage(QRectF(0, 0, 20, 15), self.imageObj, QRectF(0, 0, 40.0, 30.0))

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 20, 15).normalized()


class FilterIconItem(QGraphicsItem):
    def __init__(self, parent, imageObj):
        super().__init__(parent)
        self.grNode = parent
        self.imageObj = imageObj
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent, False)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        view = self.grNode.node.scene.getView()

        zoom = int(self.grNode.node.scene.getView().zoom - self.grNode.node.scene.getView().startZoom)
        faktor = self.grNode.node.scene.getView().zoomInFactor
        zoomFaktor = float(faktor) ** zoom
        scaleFaktor = self.grNode.scale()

        viewPos = view.mapToGlobal(QPoint(0, 0))
        grNodePos = view.mapFromScene(self.grNode.pos().x(), self.grNode.pos().y())
        angle = self.grNode.rotation()
        newX = (event.pos().x() + self.pos().x()) * math.cos(math.radians(angle)) - \
               (event.pos().y() + self.pos().y()) * math.sin(math.radians(angle))
        newY = (event.pos().x() + self.pos().x()) * math.sin(math.radians(angle)) + \
               (event.pos().y() + self.pos().y()) * math.cos(math.radians(angle))
        eventPos = QPoint(int(newX * zoomFaktor * scaleFaktor),
                          int(newY * zoomFaktor * scaleFaktor))
        actionPos = viewPos + grNodePos + eventPos
        self.grNode.filterWindowPressed(actionPos.x(), actionPos.y())

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if self.grNode.node.locked:
            return
        painter.drawImage(QRectF(0, 0, 15, 15), self.imageObj, QRectF(0, 0, 32.0, 32.0))

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 20, 15).normalized()


class OptionIconItem(QGraphicsItem):
    def __init__(self, parent, imageObj):
        super().__init__(parent)
        self.grNode = parent
        self.imageObj = imageObj
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemStacksBehindParent, False)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        view = self.grNode.node.scene.getView()

        zoom = int(self.grNode.node.scene.getView().zoom - self.grNode.node.scene.getView().startZoom)
        faktor = self.grNode.node.scene.getView().zoomInFactor
        zoomFaktor = float(faktor) ** zoom
        scaleFaktor = self.grNode.scale()

        viewPos = view.mapToGlobal(QPoint(0, 0))
        grNodePos = view.mapFromScene(self.grNode.pos().x(), self.grNode.pos().y())
        angle = self.grNode.rotation()
        newX = (event.pos().x() + self.pos().x()) * math.cos(math.radians(angle)) - \
               (event.pos().y() + self.pos().y()) * math.sin(math.radians(angle))
        newY = (event.pos().x() + self.pos().x()) * math.sin(math.radians(angle)) + \
               (event.pos().y() + self.pos().y()) * math.cos(math.radians(angle))
        eventPos = QPoint(int(newX * zoomFaktor * scaleFaktor),
                          int(newY * zoomFaktor * scaleFaktor))
        actionPos = viewPos + grNodePos + eventPos
        self.grNode.optionWindowPressed(actionPos.x(), actionPos.y())

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if self.grNode.node.locked:
            return
        painter.drawImage(QRectF(0, 0, 15, 15), self.imageObj, QRectF(0, 0, 32.0, 32.0))

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 20, 15).normalized()