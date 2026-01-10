from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor

class Handle(QGraphicsRectItem):
    """Pontos de controle nos vértices e extremidades para redimensionamento"""
    def __init__(self, parent, position_name):
        # Criamos um handle de 10x10 pixels
        super().__init__(-5, -5, 10, 10, parent)
        self.parent_node = parent
        self.pos_name = position_name
        self.setBrush(QColor("#f2f71d")) # Amarelo AmareloMind
        self.setPen(QPen(QColor("#1a1a1a"), 1))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setZValue(100)
        self.setCursor(self._get_cursor())

    def _get_cursor(self):
        """Define o cursor do mouse baseado na posição do handle"""
        cursors = {
            'h1': Qt.SizeFDiagCursor, 'h2': Qt.SizeVerCursor,
            'h3': Qt.SizeBDiagCursor, 'h4': Qt.SizeHorCursor,
            'h5': Qt.SizeHorCursor, 'h6': Qt.SizeBDiagCursor,
            'h7': Qt.SizeVerCursor, 'h8': Qt.SizeFDiagCursor
        }
        return cursors.get(self.pos_name, Qt.ArrowCursor)

    def mouseMoveEvent(self, event):
        """Passa a lógica de movimento para o nó pai"""
        new_pos = self.mapToParent(event.pos())
        self.parent_node.resize_logic(self.pos_name, new_pos)

class MindMapNode(QGraphicsRectItem):
    def __init__(self, x, y):
        super().__init__(0, 0, 150, 80)
        self.setPos(x, y)
        self.min_width, self.min_height = 80, 40
        
        # Elemento de Texto Interno
        self.text_item = QGraphicsTextItem("Digite aqui...", self)
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        
        self.setFlags(
            QGraphicsItem.ItemIsMovable | 
            QGraphicsItem.ItemIsSelectable | 
            QGraphicsItem.ItemSendsGeometryChanges
        )
        
        # Dicionário com os 8 handles de redimensionamento
        self.handles = {p: Handle(self, p) for p in [
            'h1', 'h2', 'h3',  # Topo (Esquerda, Centro, Direita)
            'h4', 'h5',        # Meio (Esquerda, Direita)
            'h6', 'h7', 'h8'   # Base (Esquerda, Centro, Direita)
        ]}
        
        self.update_handle_positions()
        self.set_handles_visible(False)

    def update_handle_positions(self):
        """Reposiciona os handles conforme o retângulo do nó muda"""
        r = self.rect()
        self.handles['h1'].setPos(r.topLeft())
        self.handles['h2'].setPos(r.center().x(), r.top())
        self.handles['h3'].setPos(r.topRight())
        self.handles['h4'].setPos(r.left(), r.center().y())
        self.handles['h5'].setPos(r.right(), r.center().y())
        self.handles['h6'].setPos(r.bottomLeft())
        self.handles['h7'].setPos(r.center().x(), r.bottom())
        self.handles['h8'].setPos(r.bottomRight())
        self.center_text()

    def center_text(self):
        """Garante que o texto esteja sempre no meio do nó"""
        r = self.rect()
        tr = self.text_item.boundingRect()
        self.text_item.setPos(r.center().x() - tr.width()/2, 
                             r.center().y() - tr.height()/2)

    def resize_logic(self, name, pos):
        """Lógica matemática para redimensionar mantendo a integridade do objeto"""
        r = self.rect()
        # Redimensionamento para a Direita/Baixo (Simples)
        if name == 'h8': r.setBottomRight(pos)
        elif name == 'h5': r.setRight(pos.x())
        elif name == 'h7': r.setBottom(pos.y())
        # Redimensionamento para a Esquerda/Topo (Exige mover a posição do item)
        elif name == 'h1': r.setTopLeft(pos)
        elif name == 'h4': r.setLeft(pos.x())
        elif name == 'h2': r.setTop(pos.y())
        elif name == 'h3': r.setTopRight(pos)
        elif name == 'h6': r.setBottomLeft(pos)

        if r.width() >= self.min_width and r.height() >= self.min_height:
            self.setRect(r.normalized())
            self.update_handle_positions()

    def set_handles_visible(self, visible):
        for h in self.handles.values(): h.setVisible(visible)

    def itemChange(self, change, value):
        """Notifica o sistema quando o nó é selecionado ou movido"""
        if change == QGraphicsItem.ItemSelectedChange:
            self.set_handles_visible(bool(value))
        
        # Sincronização com conexões (SmartConnection)
        if change == QGraphicsItem.ItemPositionHasChanged:
            if self.scene():
                # Import dinâmico para evitar dependência circular
                from core.connection import SmartConnection
                for item in self.scene().items():
                    if isinstance(item, SmartConnection):
                        if item.source == self or item.target == self:
                            item.update_path()
                            
        return super().itemChange(change, value)