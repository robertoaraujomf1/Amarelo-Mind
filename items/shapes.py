from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QLinearGradient, QColor, QBrush, QPen, QPainter
from PySide6.QtCore import Qt, QRectF
from items.base_node import MindMapNode

class StyledNode(MindMapNode):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        # 1. Configuração do Texto (Contraste Moderno)
        self.text_item.setDefaultTextColor(QColor("#1a1a1a")) # Grafite escuro para leitura
        font = self.text_item.font()
        font.setPointSize(10)
        font.setBold(True)
        font.setFamily("Segoe UI")
        self.text_item.setFont(font)
        
        # 2. Efeito de Sombra (Profundidade)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(4, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

    def paint(self, painter, option, widget):
        """Aplica o design visual profissional (AmareloMind Design)"""
        r = self.rect()
        
        # Gradiente Linear Amarelo Vibrante para Amarelo Ouro
        gradient = QLinearGradient(r.topLeft(), r.bottomLeft())
        gradient.setColorAt(0, QColor("#f2f71d")) # Amarelo Mind principal
        gradient.setColorAt(1, QColor("#d4d912")) # Tom mais escuro para volume
        
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Desenho do Corpo Arredondado (Curvas modernas)
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor("#a1a510"), 1.5)) # Borda sutil
        painter.drawRoundedRect(r, 12, 12) # Cantos com 12px de curva

        # 3. Feedback de Seleção (Borda de Destaque Futurista)
        if self.isSelected():
            painter.setPen(QPen(QColor("#ffffff"), 2, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            # Desenha uma borda externa branca tracejada
            painter.drawRoundedRect(r.adjusted(-4, -4, 4, 4), 14, 14)
            
            # Brilho extra no amarelo quando selecionado
            painter.setPen(QPen(QColor("#f2f71d"), 1))
            painter.drawRoundedRect(r.adjusted(-1, -1, 1, 1), 12, 12)

    def set_image(self, file_path):
        """Função para o Botão Mídia (suporte futuro dentro do StyledNode)"""
        # Esta lógica pode ser expandida aqui sem tocar no main ou base_node
        from PySide6.QtGui import QPixmap
        pixmap = QPixmap(file_path)
        # Lógica de exibição de imagem...