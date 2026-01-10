import sys
import os
from PySide6.QtWidgets import (QMainWindow, QApplication, QGraphicsView, 
                             QGraphicsScene, QFileDialog, QToolBar,
                             QStatusBar, QWidget, QHBoxLayout, QLineEdit, 
                             QLabel, QFrame, QStyle)
from PySide6.QtCore import Qt, QRectF, QSize, QPointF
from PySide6.QtGui import QPainter, QColor, QImage, QIcon, QAction, QWheelEvent

# Importações dos módulos que seguem a mesma regra de blindagem
try:
    from items.shapes import StyledNode as MindMapNode
    from core.connection import SmartConnection
except ImportError:
    MindMapNode = None
    SmartConnection = None

class CustomView(QGraphicsView):
    """Gerencia Zoom e Navegação"""
    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

class AmareloMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Amarelo Mind")
        self.resize(1280, 720)
        
        # Design Moderno: Fundo Grafite com acentos em Amarelo
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QToolBar { 
                background-color: #1e1e1e; 
                border-bottom: 2px solid #f2f71d; 
                spacing: 20px; 
                padding: 8px;
            }
            QStatusBar { 
                background-color: #1e1e1e; 
                color: #f2f71d; 
                font-family: 'Segoe UI', sans-serif;
                border-top: 1px solid #333;
            }
            QLabel { color: #888888; font-size: 10px; font-weight: bold; }
            QLineEdit { 
                background-color: #2d2d2d; 
                color: #f2f71d; 
                border: 1px solid #444; 
                border-radius: 4px; 
                padding: 4px;
            }
            QLineEdit:focus { border: 1px solid #f2f71d; }
        """)

        # 1. Canvas
        self.scene = QGraphicsScene(-5000, -5000, 10000, 10000)
        self.view = CustomView(self.scene)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self.view.setBackgroundBrush(QColor("#1a1a1a"))
        self.view.setFrameStyle(QFrame.NoFrame)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.view)

        # 2. Interface
        self.setup_toolbar()
        self.setup_statusbar()
        
        self.scene.selectionChanged.connect(self.on_selection_changed)

    def setup_toolbar(self):
        """Toolbar Moderna com ícones corrigidos para PySide6"""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(28, 28))
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # SP_FileIcon -> Adicionar Nó
        icon_node = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        self.act_add = QAction(icon_node, "", self)
        self.act_add.setToolTip("Novo Nó (N)")
        self.act_add.setShortcut("N")
        self.act_add.triggered.connect(self.add_node)
        self.toolbar.addAction(self.act_add)

        # SP_CommandLink -> Conectar
        icon_conn = self.style().standardIcon(QStyle.StandardPixmap.SP_CommandLink)
        self.act_conn = QAction(icon_conn, "", self)
        self.act_conn.setToolTip("Conectar Selecionados (C)")
        self.act_conn.setShortcut("C")
        self.act_conn.triggered.connect(self.connect_nodes)
        self.toolbar.addAction(self.act_conn)

        self.toolbar.addSeparator()

        # SP_DialogSaveButton -> Exportar
        icon_exp = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        self.act_exp = QAction(icon_exp, "", self)
        self.act_exp.setToolTip("Exportar Imagem (Ctrl+E)")
        self.act_exp.setShortcut("Ctrl+E")
        self.act_exp.triggered.connect(self.export_map)
        self.toolbar.addAction(self.act_exp)

    def setup_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 0, 15, 5)
        
        self.in_x = QLineEdit(); self.in_y = QLineEdit()
        self.in_w = QLineEdit(); self.in_h = QLineEdit()
        self.inputs = {"X": self.in_x, "Y": self.in_y, "W": self.in_w, "H": self.in_h}

        for label, edit in self.inputs.items():
            layout.addWidget(QLabel(label))
            edit.setFixedWidth(60)
            edit.returnPressed.connect(self.apply_manual_changes)
            layout.addWidget(edit)

        self.status.addPermanentWidget(container)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            for item in self.scene.selectedItems():
                self.scene.removeItem(item)
        elif event.key() == Qt.Key.Key_Escape:
            self.scene.clearSelection()
        super().keyPressEvent(event)

    def on_selection_changed(self):
        sel = self.scene.selectedItems()
        if len(sel) == 1 and hasattr(sel[0], 'rect'):
            node = sel[0]
            self.in_x.setText(str(int(node.pos().x())))
            self.in_y.setText(str(int(node.pos().y())))
            self.in_w.setText(str(int(node.rect().width())))
            self.in_h.setText(str(int(node.rect().height())))
        else:
            for edit in self.inputs.values(): edit.clear()

    def apply_manual_changes(self):
        sel = self.scene.selectedItems()
        if len(sel) == 1:
            try:
                node = sel[0]
                node.setPos(float(self.in_x.text()), float(self.in_y.text()))
                node.setRect(0, 0, float(self.in_w.text()), float(self.in_h.text()))
                if hasattr(node, 'update_handle_positions'):
                    node.update_handle_positions()
            except ValueError: pass

    def add_node(self):
        if MindMapNode:
            center = self.view.mapToScene(self.view.viewport().rect().center())
            node = MindMapNode(center.x() - 75, center.y() - 40)
            self.scene.addItem(node)

    def connect_nodes(self):
        sel = self.scene.selectedItems()
        if len(sel) == 2 and SmartConnection:
            conn = SmartConnection(sel[0], sel[1])
            self.scene.addItem(conn)

    def export_map(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar Mapa", "", "PNG (*.png)")
        if path:
            rect = self.scene.itemsBoundingRect().adjusted(-50, -50, 50, 50)
            img = QImage(rect.size().toSize(), QImage.Format_ARGB32)
            img.fill(QColor("#1a1a1a"))
            painter = QPainter(img)
            painter.setRenderHint(QPainter.Antialiasing)
            self.scene.render(painter, QRectF(img.rect()), rect)
            painter.end()
            img.save(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AmareloMainWindow()
    window.show()
    sys.exit(app.exec())