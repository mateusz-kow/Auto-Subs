from PySide6.QtWidgets import QVBoxLayout, QPushButton, QCheckBox, QColorDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal
from src.utils.color_operations import ass_to_qcolor, qcolor_to_ass


class HighlightStyleLayout(QVBoxLayout):
    """
    Layout providing UI controls for configuring subtitle highlight styles
    using a dictionary format instead of raw ASS tags.
    """

    settings_changed = Signal(object)

    def __init__(self, style: dict):
        super().__init__()

        self.highlight_color = QColor("#ffcc99")
        self.highlight_border_color = QColor("#000000")

        self.highlight_color_button = QPushButton("Highlight Color (Text)")
        self.highlight_color_button.setStyleSheet(f"background-color: {self.highlight_color.name()}")
        self.highlight_color_button.clicked.connect(self.select_highlight_color)
        self.addWidget(self.highlight_color_button)

        self.highlight_border_button = QPushButton("Highlight Color (Border)")
        self.highlight_border_button.setStyleSheet(f"background-color: {self.highlight_border_color.name()}")
        self.highlight_border_button.clicked.connect(self.select_highlight_border_color)
        self.addWidget(self.highlight_border_button)

        self.fade_highlight_checkbox = QCheckBox("Fade Highlight In/Out")
        self.fade_highlight_checkbox.stateChanged.connect(self.settings_changed.emit)
        self.addWidget(self.fade_highlight_checkbox)

        self.set_settings(style)

    def select_highlight_color(self):
        color = QColorDialog.getColor(self.highlight_color)
        if color.isValid() and color != self.highlight_color:
            self.highlight_color = color
            self.highlight_color_button.setStyleSheet(f"background-color: {color.name()}")
            self.settings_changed.emit(self.get_settings())

    def select_highlight_border_color(self):
        color = QColorDialog.getColor(self.highlight_border_color)
        if color.isValid() and color != self.highlight_border_color:
            self.highlight_border_color = color
            self.highlight_border_button.setStyleSheet(f"background-color: {color.name()}")
            self.settings_changed.emit(self.get_settings())

    def get_settings(self) -> dict:
        """
        Return the highlight style as a dictionary.
        """
        return {
            "highlight_style": {
                "text_color": qcolor_to_ass(self.highlight_color),
                "border_color": qcolor_to_ass(self.highlight_border_color),
                "fade": self.fade_highlight_checkbox.isChecked()
            }
        }

    def set_settings(self, settings: dict):
        """
        Apply highlight style from dictionary settings.
        """
        style = settings.get("highlight_style", {})

        # Set text color
        if "text_color" in style:
            self.highlight_color = ass_to_qcolor(style["text_color"])
            self.highlight_color_button.setStyleSheet(f"background-color: {self.highlight_color.name()}")

        # Set border color
        if "border_color" in style:
            self.highlight_border_color = ass_to_qcolor(style["border_color"])
            self.highlight_border_button.setStyleSheet(f"background-color: {self.highlight_border_color.name()}")

        # Set fade
        if "fade" in style:
            self.fade_highlight_checkbox.setChecked(bool(style["fade"]))
