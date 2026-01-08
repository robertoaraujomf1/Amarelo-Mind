from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsTextItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QCursor

class Handle(QGraphicsRectItem):
    """Os pequenos quadrados h1-h8 para redimensionar"""
    def __init__(self, parent, position_name):
        super().__init__(-5, -5, 10, 10, parent)
        self.parent_node = parent
        self.pos_name = position_name
        self.setBrush(Qt.white)
        self.setPen(QPen(Qt.black, 1))
        
        # Flags para detecção de movimento
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # Define o cursor apropriado para cada handle
        self.setCursor(self._get_handle_cursor())

    def _get_handle_cursor(self):
        cursors = {
            'h1': Qt.SizeFDiagCursor, 'h3': Qt.SizeBDiagCursor,
            'h6': Qt.SizeBDiagCursor, 'h8': Qt.SizeFDiagCursor,
            'h2': Qt.SizeVerCursor, 'h7': Qt.SizeVerCursor,
            'h4': Qt.SizeHorCursor, 'h5': Qt.SizeHorCursor
        }
        return cursors.get(self.pos_name, Qt.ArrowCursor)

    def mouseMoveEvent(self, event):
        # Envia a posição mapeada para o sistema de coordenadas do pai
        new_pos = self.mapToParent(event.pos())
        self.parent_node.resize_logic(self.pos_name, new_pos)

class MindMapNode(QGraphicsRectItem):
    def __init__(self, x, y):
        super().__init__(0, 0, 150, 80)
        self.setPos(x, y)
        self.min_width = 100
        self.min_height = 50
        self.padding = 5 # Margem interna padrão (aprox 0.2mm)
        
        # Elemento de texto interno
        self.text_item = QGraphicsTextItem("", self)
        self.text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        
        self.setFlags(QGraphicsItem.ItemIsMovable | 
                      QGraphicsItem.ItemIsSelectable | 
                      QGraphicsItem.ItemSendsGeometryChanges)
        
        self.handles = {}
        self.init_handles()
        self.set_handles_visible(False) # Visíveis apenas quando selecionado

    def init_handles(self):
        positions = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8']
        for p in positions:
            self.handles[p] = Handle(self, p)
        self.update_handle_positions()

    def update_handle_positions(self):
        r = self.rect()
        self.handles['h1'].setPos(r.topLeft())
        self.handles['h2'].setPos(r.center().x(), r.top())
        self.handles['h3'].setPos(r.topRight())
        self.handles['h4'].setPos(r.left(), r.center().y())
        self.handles['h5'].setPos(r.right(), r.center().y())
        self.handles['h6'].setPos(r.bottomLeft())
        self.handles['h7'].setPos(r.center().x(), r.bottom())
        self.handles['h8'].setPos(r.bottomRight())

    def resize_logic(self, handle_name, new_pos):
        r = self.rect()
        new_rect = QRectF(r)
        
        # Verifica se o redimensionamento deve ser proporcional (cantos)
        is_proportional = handle_name in ['h1', 'h3', 'h6', 'h8']
        aspect_ratio = r.width() / r.height() if r.height() != 0 else 1

        # Lógica simplificada para o lado inferior direito (h8 e h5, h7)
        if handle_name == 'h8':
            w = max(new_pos.x(), self.min_width)
            h = w / aspect_ratio if is_proportional else max(new_pos.y(), self.min_height)
            new_rect.setBottomRight(QPointF(w, h))
        
        elif handle_name == 'h5': # Redimensionamento livre horizontal
            new_rect.setRight(max(new_pos.x(), self.min_width))
            
        elif handle_name == 'h7': # Redimensionamento livre vertical
            new_rect.setBottom(max(new_pos.y(), self.min_height))

        # Bloqueio de tamanho mínimo baseado no conteúdo visível (Observação 2)
        text_rect = self.text_item.boundingRect()
        min_w = max(self.min_width, text_rect.width() + self.padding * 2)
        min_h = max(self.min_height, text_rect.height() + self.padding * 2)
        
        if new_rect.width() < min_w: new_rect.setWidth(min_w)
        if new_rect.height() < min_h: new_rect.setHeight(min_h)

        self.setRect(new_rect)
        self.update_handle_positions()
        self.update_text_layout()

    def update_text_layout(self):
        """Justapõe o texto dentro do perímetro do objeto"""
        r = self.rect()
        available_w = r.width() - (self.padding * 2)
        self.text_item.setTextWidth(available_w)
        self.text_item.setPos(self.padding, self.padding)

    def set_handles_visible(self, visible):
        for h in self.handles.values():
            h.setVisible(visible)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            self.set_handles_visible(bool(value))
        return super().itemChange(change, value)