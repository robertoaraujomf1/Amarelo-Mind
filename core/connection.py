from PySide6.QtWidgets import QGraphicsLineItem
from PySide6.QtCore import QLineF, Qt
from PySide6.QtGui import QPen, QColor

class SmartConnection(QGraphicsLineItem):
    def __init__(self, source, target):
        super().__init__()
        self.source = source
        self.target = target
        self.setPen(QPen(QColor("#0078d4"), 3, Qt.SolidLine, Qt.RoundCap))
        self.setZValue(-1) # Fica atrás dos objetos
        self.update_path()

    def update_path(self):
        # Conecta o centro do objeto A ao centro do objeto B
        line = QLineF(self.source.sceneBoundingRect().center(), 
                     self.target.sceneBoundingRect().center())
        self.setLine(line)

    def paint(self, painter, option, widget):
        self.update_path() # Força a atualização visual em tempo real
        super().paint(painter, option, widget)