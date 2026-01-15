import sys
import os
import json
from PySide6.QtWidgets import (QMainWindow, QApplication, QGraphicsView, 
                             QGraphicsScene, QFileDialog, QToolBar,
                             QStatusBar, QWidget, QFrame, QStyle, 
                             QFontDialog, QColorDialog, QGraphicsDropShadowEffect,
                             QCheckBox)
from PySide6.QtCore import Qt, QRectF, QSize, QPointF, QPoint
from PySide6.QtGui import (QPainter, QColor, QImage, QIcon, QAction, QLinearGradient,
                          QWheelEvent, QKeyEvent, QUndoStack, QPen, QFont, QPixmap, QBrush)

# --- IMPORTAÇÃO DOS COMPONENTES CORE ---
try:
    from items.shapes import StyledNode as MindMapNode 
    from core.connection import SmartConnection
except ImportError:
    # Caso os arquivos core ainda não estejam linkados, usamos um placeholder funcional
    from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
    class MindMapNode(QGraphicsRectItem):
        def __init__(self, x, y):
            super().__init__(0, 0, 150, 80)
            self.setPos(x, y)
            self.setFlags(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable | QGraphicsRectItem.ItemSendsGeometryChanges)
            self.setBrush(QColor("#f2f71d"))
            self.text_item = QGraphicsTextItem("Texto", self)
            self.text_item.setPos(10, 25)

        def itemChange(self, change, value):
            # Implementação do MAGNETISMO (Snap to Grid)
            if change == QGraphicsRectItem.ItemPositionChange:
                # Verifica se a checkbox global de magnetismo está ativa
                main_win = QApplication.activeWindow()
                if hasattr(main_win, 'cb_magnetismo') and main_win.cb_magnetismo.isChecked():
                    grid_size = 20
                    new_pos = value
                    x = round(new_pos.x() / grid_size) * grid_size
                    y = round(new_pos.y() / grid_size) * grid_size
                    return QPointF(x, y)
            return super().itemChange(change, value)

class InfiniteCanvas(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self.setBackgroundBrush(QColor("#f5f6fA")) 
        self.setFrameStyle(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Eliminação de rastros
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self._is_panning = False
        self._last_pan_pos = QPoint()

    def wheelEvent(self, event: QWheelEvent):
        # Zoom com a roda (Scroll desativado conforme pedido)
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        # Botão direito move a tela
        if event.button() == Qt.RightButton and not item:
            self._is_panning = True
            self._last_pan_pos = event.position().toPoint()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        # Botão esquerdo seleciona ou move
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag if item else QGraphicsView.RubberBandDrag)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            delta = event.position().toPoint() - self._last_pan_pos
            self._last_pan_pos = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._is_panning = False
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

class AmareloMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Amarelo Mind")
        self.undo_stack = QUndoStack(self)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f6fA; }
            QToolBar { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #e8e8e8);
                border-bottom: 1px solid #ccc; padding: 5px; 
            }
        """)

        self.scene = QGraphicsScene(-10000, -10000, 20000, 20000)
        self.view = InfiniteCanvas(self.scene, self)
        self.setCentralWidget(self.view)
        
        self.setup_toolbar()
        self.showMaximized()

    # --- ÍCONES ---

    def draw_obj_icon(self):
        pixmap = QPixmap(100, 100); pixmap.fill(Qt.transparent)
        p = QPainter(pixmap); p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#f2f71d")); p.setPen(QPen(Qt.black, 4))
        p.drawRoundedRect(20, 30, 60, 40, 5, 5)
        p.end(); return QIcon(pixmap)

    def draw_connect_icon(self):
        pixmap = QPixmap(100, 100); pixmap.fill(Qt.transparent)
        p = QPainter(pixmap); p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor("#0078d4"), 10, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(20, 20, 40, 60, 90*16, 180*16)
        p.drawArc(40, 20, 40, 60, -90*16, 180*16)
        p.end(); return QIcon(pixmap)

    def setup_toolbar(self):
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(42, 42))
        self.addToolBar(self.toolbar)

        # 1. Salvar e Abrir
        self.toolbar.addAction(QAction(self.style().standardIcon(QStyle.SP_DialogOpenButton), "Abrir", self, triggered=self.open_project))
        self.toolbar.addAction(QAction(self.style().standardIcon(QStyle.SP_DriveHDIcon), "Salvar Como", self, triggered=self.save_project))
        self.toolbar.addSeparator()

        # MAGNETISMO CHECKBOX
        self.cb_magnetismo = QCheckBox("Magnetismo")
        self.cb_magnetismo.setStyleSheet("margin-left: 10px; font-weight: bold;")
        self.cb_magnetismo.stateChanged.connect(self.apply_grid_now)
        self.toolbar.addWidget(self.cb_magnetismo)
        self.toolbar.addSeparator()

        # Edição
        self.toolbar.addAction(QAction(self.style().standardIcon(QStyle.SP_ArrowBack), "Undo", self, triggered=self.undo_stack.undo))
        self.toolbar.addAction(QAction(self.draw_obj_icon(), "Adicionar Objeto", self, triggered=self.add_node))
        self.toolbar.addAction(QAction(self.draw_connect_icon(), "Conectar", self, triggered=self.connect))
        self.toolbar.addAction(QAction(self.style().standardIcon(QStyle.SP_TrashIcon), "Excluir", self, triggered=self.delete_sel))
        
        self.toolbar.addSeparator()
        self.toolbar.addAction(QAction(self.style().standardIcon(QStyle.SP_FileDialogListView), "Fonte", self, triggered=self.unified_font))
        self.toolbar.addAction(QAction(self.style().standardIcon(QStyle.SP_DialogResetButton), "Cor", self, triggered=self.apply_color))
        self.toolbar.addAction(QAction(self.style().standardIcon(QStyle.SP_TitleBarContextHelpButton), "Sombra", self, triggered=self.handle_shadow))

    # --- LÓGICA ---

    def apply_grid_now(self, state):
        if state == Qt.Checked:
            grid = 20
            for item in self.scene.items():
                if isinstance(item, MindMapNode):
                    x = round(item.x() / grid) * grid
                    y = round(item.y() / grid) * grid
                    item.setPos(x, y)

    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar", "", "Arquivo Amarelo (*.amarelo)")
        if path:
            data = [{"pos": [i.x(), i.y()], "text": i.text_item.toPlainText()} for i in self.scene.items() if isinstance(i, MindMapNode)]
            with open(path, 'w') as f: json.dump(data, f)

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir", "", "Arquivo Amarelo (*.amarelo)")
        if path:
            self.scene.clear()
            with open(path, 'r') as f:
                for n in json.load(f):
                    node = MindMapNode(n["pos"][0], n["pos"][1])
                    node.text_item.setPlainText(n["text"])
                    self.scene.addItem(node)

    def unified_font(self):
        sel = self.scene.selectedItems()
        if not sel: return
        ok, font = QFontDialog.getFont(self)
        if ok:
            color = QColorDialog.getColor(Qt.black, self)
            for item in sel:
                if hasattr(item, 'text_item'):
                    item.text_item.setFont(font)
                    item.text_item.setDefaultTextColor(color)

    def apply_color(self):
        sel = self.scene.selectedItems()
        if not sel: return
        color = QColorDialog.getColor(Qt.yellow, self)
        if color.isValid():
            for item in sel:
                if isinstance(item, MindMapNode): item.setBrush(QBrush(color))

    def handle_shadow(self):
        for item in self.scene.selectedItems():
            if item.graphicsEffect():
                item.setGraphicsEffect(None)
            else:
                s = QGraphicsDropShadowEffect(); s.setBlurRadius(15); s.setOffset(5, 5)
                item.setGraphicsEffect(s)
        self.view.viewport().update()

    def add_node(self):
        node = MindMapNode(self.view.mapToScene(self.view.rect().center()).x(), 
                           self.view.mapToScene(self.view.rect().center()).y())
        self.scene.addItem(node)

    def connect(self):
        sel = self.scene.selectedItems()
        if len(sel) >= 2:
            try:
                conn = SmartConnection(sel[0], sel[1])
                self.scene.addItem(conn)
            except: pass

    def delete_sel(self):
        for i in self.scene.selectedItems(): self.scene.removeItem(i)

    def export_png(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar", "", "PNG (*.png)")
        if path:
            rect = self.scene.itemsBoundingRect()
            img = QImage(rect.size().toSize(), QImage.Format_ARGB32); img.fill(Qt.white)
            p = QPainter(img); self.scene.render(p, QRectF(img.rect()), rect); p.end()
            img.save(path)

if __name__ == "__main__":
    app = QApplication(sys.argv); win = AmareloMainWindow(); win.show(); sys.exit(app.exec())