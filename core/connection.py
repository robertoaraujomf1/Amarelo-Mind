from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PySide6.QtGui import QPainterPath, QPen, QColor, QPainter
from PySide6.QtCore import Qt, QPointF

class SmartConnection(QGraphicsPathItem):
    """Linhas de conexão inteligentes com curvas suaves de Bézier"""
    def __init__(self, source_node, target_node):
        super().__init__()
        self.source = source_node
        self.target = target_node
        
        # Estilo da Linha: Grafite moderno, semi-transparente para elegância
        self.setPen(QPen(QColor(180, 180, 180, 200), 2, Qt.SolidLine, Qt.RoundCap))
        
        # Garante que a linha fique sempre atrás dos nós
        self.setZValue(-1)
        
        # Impede que a linha seja selecionada ou movida individualmente
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        
        self.update_path()

    def update_path(self):
        """Calcula a geometria da curva entre os dois nós em tempo real"""
        if not self.source or not self.target:
            return

        path = QPainterPath()
        
        # Pega os centros dos retângulos dos nós na cena
        p1 = self.source.sceneBoundingRect().center()
        p2 = self.target.sceneBoundingRect().center()
        
        path.moveTo(p1)
        
        # Lógica de Curvatura (S-Curve):
        # Criamos dois pontos de controle baseados na distância horizontal
        dx = p2.x() - p1.x()
        dist_ajustada = dx * 0.5
        
        # Ponto de controle 1 (estica horizontalmente a partir do nó de origem)
        ctrl1 = QPointF(p1.x() + dist_ajustada, p1.y())
        # Ponto de controle 2 (chega horizontalmente no nó de destino)
        ctrl2 = QPointF(p2.x() - dist_ajustada, p2.y())
        
        # Desenha a curva cúbica
        path.cubicTo(ctrl1, ctrl2, p2)
        
        self.setPath(path)

    def paint(self, painter, option, widget):
        """Renderiza a linha com máxima suavização"""
        painter.setRenderHint(QPainter.Antialiasing)
        super().paint(painter, option, widget)