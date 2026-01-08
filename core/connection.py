from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PySide6.QtGui import QPainterPath, QPen, QColor
from PySide6.QtCore import QPointF, Qt

class SmartConnection(QGraphicsPathItem):
    def __init__(self, source_node, target_node):
        super().__init__()
        self.source = source_node
        self.target = target_node
        
        # Estilo da linha (Cor padrão escura, curva suave)
        self.line_color = QColor("#444444")
        self.setZValue(-1)  # Garante que a linha fique atrás dos objetos
        self.setPen(QPen(self.line_color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        self.update_path()

    def update_path(self):
        """Calcula a trajetória curva desviando de obstáculos."""
        path = QPainterPath()
        
        # Pontos de ancoragem (bordas dos objetos, não o centro exato)
        start_rect = self.source.sceneBoundingRect()
        target_rect = self.target.sceneBoundingRect()
        
        start = start_rect.center()
        end = target_rect.center()

        # Definição do desvio de 1cm (aprox. 38 pixels)
        margin = 38 

        # Ponto de controle inicial para a curva de Bézier
        # Calculamos um ponto intermediário
        mid_x = (start.x() + end.x()) / 2
        mid_y = (start.y() + end.y()) / 2
        ctrl_point = QPointF(mid_x, mid_y - 100) # Curva para cima por padrão

        # Lógica de Desvio de Obstáculos
        # Verificamos se há algum objeto no caminho direto
        scene = self.source.scene()
        if scene:
            # Pegamos todos os itens que colidem com a linha teórica
            path_test = QPainterPath()
            path_test.moveTo(start)
            path_test.lineTo(end)
            obstacles = scene.items(path_test)

            for item in obstacles:
                # Se o item for um objeto (e não a própria linha ou os nodes conectados)
                if isinstance(item, QGraphicsItem) and item not in [self.source, self.target, self]:
                    obs_rect = item.sceneBoundingRect()
                    
                    # Se o objeto estiver no caminho, empurramos o ponto de controle
                    # para manter a distância de 1cm (margin) do perímetro do obstáculo
                    if obs_rect.contains(ctrl_point):
                        ctrl_point.setY(obs_rect.top() - margin)
                    
                    # Evitar sobreposição lateral
                    if abs(ctrl_point.x() - obs_rect.center().x()) < margin:
                        ctrl_point.setX(obs_rect.right() + margin)

        # Construção da Curva de Bézier Quadrática
        path.moveTo(start)
        path.quadTo(ctrl_point, end)
        
        self.setPath(path)

    def change_color(self, new_color_hex):
        """Método para o Botão 12 (Cor das conexões)"""
        self.line_color = QColor(new_color_hex)
        self.setPen(QPen(self.line_color, 2))