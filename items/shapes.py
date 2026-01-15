from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QApplication
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPen, QBrush

class StyledNode(QGraphicsRectItem):
    def __init__(self, x, y, text="Novo Objeto"):
        super().__init__(0, 0, 160, 60)
        self.setPos(x, y)
        self.setFlags(QGraphicsRectItem.ItemIsMovable | 
                      QGraphicsRectItem.ItemIsSelectable | 
                      QGraphicsRectItem.ItemSendsGeometryChanges)
        
        self.setBrush(QBrush(QColor("#f2f71d")))
        self.setPen(QPen(Qt.black, 2))
        
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setPos(10, 15)
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)

    def itemChange(self, change, value):
        if change == QGraphicsRectItem.ItemPositionChange:
            # Integração com a Checkbox da Main
            main_win = QApplication.activeWindow()
            if hasattr(main_win, 'cb_magnetismo') and main_win.cb_magnetismo.isChecked():
                grid = 20
                x = round(value.x() / grid) * grid
                y = round(value.y() / grid) * grid
                return QPointF(x, y)
        return super().itemChange(change, value)