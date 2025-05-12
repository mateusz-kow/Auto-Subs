from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QMenu
from src.settings.StyleManager import StyleManager
from src.utils.constants import STYLES_DIR


def reset_style_to_default():
    StyleManager().reset_to_default()


class TopBar(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(8)

        # Button: File
        self.file_btn = QPushButton("File")
        self.file_menu = QMenu(self.file_btn)
        self.file_btn.setMenu(self.file_menu)
        self.layout.addWidget(self.file_btn)

        # Button: Style
        self.style_btn = QPushButton("Style")
        self.style_menu = QMenu(self.style_btn)
        self.style_btn.setMenu(self.style_menu)
        self.layout.addWidget(self.style_btn)

        # File Menu options
        new = QAction("New", self)
        new.triggered.connect(self.create_new_file)
        open_file = QAction("Open", self)
        open_file.triggered.connect(self.open_file)
        save_file = QAction("Save", self)
        save_file.triggered.connect(self.save_style_to_file)

        self.file_menu.addAction(new)
        self.file_menu.addAction(open_file)
        self.file_menu.addAction(save_file)

        # Style Menu options
        load_style = QAction("Load Style", self)
        load_style.triggered.connect(self.load_style_from_file)
        reset_style = QAction("Reset to Default", self)
        reset_style.triggered.connect(reset_style_to_default)

        self.style_menu.addAction(load_style)
        self.style_menu.addAction(reset_style)

        self.layout.addStretch()  # Push all widgets to the left

    def create_new_file(self):
        # Placeholder for creating a new file
        QMessageBox.information(self, "New File", "Creating a new file - to be implemented.")

    def open_file(self):
        # Placeholder for opening a file
        QMessageBox.information(self, "Open File", "Opening a file - to be implemented.")

    def save_style_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Style", str(STYLES_DIR), "JSON File (*.json)")
        if path:
            StyleManager().save_to_file(path)

    def load_style_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Style", str(STYLES_DIR), "JSON File (*.json)")
        if path:
            StyleManager().load_from_file(path)
