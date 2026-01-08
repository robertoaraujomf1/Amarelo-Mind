from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPen

class Handle(QGraphicsRectItem):
    """Os pequenos quadrados h1-h8 para redimensionar"""
    def __init__(self, parent, position_name):
        super().__init__(-5, -5, 10, 10, parent)
        self.parent_node = parent
        self.pos_name = position_name
        self.setBrush(Qt.white)
        self.setPen(QPen(Qt.black, 1))
        # O handle em si não deve ser "movível" livremente, 
        # ele apenas detecta o arrasto para redimensionar o pai.
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def mouseMoveEvent(self, event):
        # Quando arrastamos o handle, enviamos a nova posição para o pai
        new_pos = self.mapToParent(event.pos())
        self.parent_node.resize_logic(self.pos_name, new_pos)

class MindMapNode(QGraphicsRectItem):
    def __init__(self, x, y):
        # Tamanho inicial padrão
        super().__init__(0, 0, 150, 80)
        self.setPos(x - 75, y - 40)
        
        # Configurações de estilo solicitadas
        self.min_width = 100
        self.min_height = 50
        self.current_colors = ["#c3c910", "#818511"]
        self.padding = 5 # 0.2mm aproximado em pixels
        
        self.setFlags(QGraphicsItem.ItemIsMovable | 
                      QGraphicsItem.ItemIsSelectable | 
                      QGraphicsItem.ItemSendsGeometryChanges)
        
        self.setPen(Qt.NoPen) # Sem borda por padrão
        self.apply_default_style()
        
        # Inicializa os handles
        self.handles = {}
        self.init_handles()
        self.hide_handles() # Ocultos por padrão até selecionar

    def apply_default_style(self):
        # Gradiente padrão #c3c910 -> #818511
        grad = QLinearGradient(0, 0, 0, self.rect().height())
        grad.setColorAt(0, QColor(self.current_colors[0]))
        grad.setColorAt(1, QColor(self.current_colors[1]))
        self.setBrush(QBrush(grad))

        # Sombra inferior e lateral esquerda (conforme requisito)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(-5, 5) # Lateral esquerda (negativo) e inferior (positivo)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)

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

        # Lógica de redimensionamento (simplificada)
        if handle_name == 'h8': # Canto inferior direito (Proporcional)
            new_rect.setRight(max(new_pos.x(), self.min_width))
            new_rect.setBottom(max(new_pos.y(), self.min_height))
        elif handle_name == 'h5': # Lateral direita (Livre)
            new_rect.setRight(max(new_pos.x(), self.min_width))
        elif handle_name == 'h7': # Base (Livre)
            new_rect.setBottom(max(new_pos.y(), self.min_height))
        # Adicione aqui as lógicas para h1-h4 conforme necessário

        self.setRect(new_rect)
        self.update_handle_positions()
        self.apply_default_style() # Recalcula o gradiente para o novo tamanho

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            if value: self.show_handles()
            else: self.hide_handles()
        return super().itemChange(change, value)

    def show_handles(self):
        for h in self.handles.values(): h.show()

    def hide_handles(self):
        for h in self.handles.values(): h.hide()

    def get_text(self): return "" # Placeholder para futura implementação de texto