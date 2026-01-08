import sys
import os
from PySide6.QtWidgets import (QMainWindow, QApplication, QToolBar, QStatusBar, 
                             QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget,
                             QFileDialog, QLineEdit, QLabel, QHBoxLayout)
from PySide6.QtCore import Qt, QSize, QPointF
from PySide6.QtGui import QIcon, QAction, QBrush, QColor, QLinearGradient

# Importações internas
try:
    from core.persistence import PersistenceManager
    from items.shapes import MindMapNode
except ImportError:
    PersistenceManager = None
    MindMapNode = None

class AmareloMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Amarelo Mind - Editor de Mapas Mentais")
        self.resize(1200, 800)
        
        # 1. Configuração da Área de Trabalho (Canvas)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-5000, -5000, 10000, 10000) 
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(Qt.Antialiasing | Qt.SmoothPixmapTransform)
        self.view.setBackgroundBrush(QBrush(QColor("#f5f0e9")))
        
        # Movimentação e arraste (Observação 1)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        
        self.setCentralWidget(self.view)
        
        # 2. Interface
        self.setup_toolbar()
        self.setup_statusbar()
        self.apply_styles()

        self.scene.selectionChanged.connect(self.on_selection_changed)

    def setup_toolbar(self):
        toolbar = QToolBar("Ferramentas")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        actions = [
            ("Novo", "assets/icons/new.png", self.new_file),
            ("Abrir", "assets/icons/open.png", self.open_file),
            ("Salvar", "assets/icons/save.png", self.save_file),
            ("Add Objeto", "assets/icons/add.png", self.add_object),
        ]

        for text, icon_path, func in actions:
            icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
            action = QAction(icon, text, self)
            action.setToolTip(text)
            action.triggered.connect(func)
            toolbar.addAction(action)

    def setup_statusbar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.setStyleSheet("background-color: #2b2b2b; color: #f5f0e9; border-top: 1px solid #c3c910;")

        self.status_container = QWidget()
        layout = QHBoxLayout(self.status_container)
        layout.setContentsMargins(5, 0, 5, 0)

        self.input_x = QLineEdit()
        self.input_y = QLineEdit()
        self.input_w = QLineEdit()
        self.input_h = QLineEdit()

        style = "background: #3d3d3d; color: #c3c910; border: 1px solid #818511; border-radius: 3px;"
        labels = ["X:", "Y:", "L:", "A:"]
        self.inputs = [self.input_x, self.input_y, self.input_w, self.input_h]

        for label_text, widget in zip(labels, self.inputs):
            layout.addWidget(QLabel(label_text))
            widget.setFixedWidth(60)
            widget.setStyleSheet(style)
            widget.returnPressed.connect(self.update_object_from_status)
            layout.addWidget(widget)

        self.status.addPermanentWidget(self.status_container)

    def on_selection_changed(self):
        selected = self.scene.selectedItems()
        if selected and len(selected) == 1:
            item = selected[0]
            self.input_x.setText(str(int(item.pos().x())))
            self.input_y.setText(str(int(item.pos().y())))
            self.input_w.setText(str(int(item.rect().width())))
            self.input_h.setText(str(int(item.rect().height())))

    def update_object_from_status(self):
        selected = self.scene.selectedItems()
        if selected and len(selected) == 1:
            item = selected[0]
            try:
                item.setPos(float(self.input_x.text()), float(self.input_y.text()))
                item.setRect(0, 0, float(self.input_w.text()), float(self.input_h.text()))
            except ValueError:
                self.status.showMessage("Erro: Valor inválido", 2000)

    def add_object(self):
        if MindMapNode:
            center = self.view.mapToScene(self.view.viewport().rect().center())
            node = MindMapNode(center.x(), center.y())
            self.scene.addItem(node)

    def keyPressEvent(self, event):
        # Botão 8: Delete
        if event.key() == Qt.Key_Delete:
            for item in self.scene.selectedItems():
                self.scene.removeItem(item)
                
        # Botão 3: Salvar (Ctrl + S)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            self.save_file()

        # Botão 10: Agrupar (Enter)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.group_selected_objects()

        # Movimentação pelas setas (Se nada estiver selecionado)
        elif not self.scene.selectedItems():
            h_bar = self.view.horizontalScrollBar()
            v_bar = self.view.verticalScrollBar()
            if event.key() == Qt.Key_Left: h_bar.setValue(h_bar.value() - 40)
            elif event.key() == Qt.Key_Right: h_bar.setValue(h_bar.value() + 40)
            elif event.key() == Qt.Key_Up: v_bar.setValue(v_bar.value() - 40)
            elif event.key() == Qt.Key_Down: v_bar.setValue(v_bar.value() + 40)

    def group_selected_objects(self):
        # Placeholder para a lógica de agrupamento (Botão 10)
        self.status.showMessage("Agrupando objetos...", 2000)

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Amarelo Mind", "", "Amarelo Mind Files (*.amind)")
        if file_path and PersistenceManager:
            PersistenceManager.save_to_file(file_path, self.scene)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Amarelo Mind", "", "Amarelo Mind Files (*.amind)")
        if file_path and PersistenceManager:
            PersistenceManager.load_from_file(file_path, self.scene)

    def new_file(self):
        os.startfile(sys.argv[0])

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; }
            QToolBar { background-color: #2b2b2b; border-bottom: 2px solid #c3c910; spacing: 15px; padding: 10px; }
            QToolButton { background-color: #3d3d3d; border: 1px solid #c3c910; border-radius: 4px; padding: 5px; }
            QToolButton:hover { background-color: #c3c910; }
            QLabel { color: #f5f0e9; font-weight: bold; }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AmareloMainWindow()
    window.showMaximized()
    sys.exit(app.exec())