from PySide6.QtWidgets import QVBoxLayout, QPushButton, QCheckBox, QColorDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal
from src.utils.color_operations import ass_to_qcolor, qcolor_to_ass


class HighlightStyleLayout(QVBoxLayout):
    """
    Layout providing UI controls for configuring subtitle highlight styles,
    including text and border colors and fade effect.
    """

    # Signal emitted when any highlight setting is changed
    settings_changed = Signal(object)

    def __init__(self):
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

    def select_highlight_color(self):
        """Open a color picker and update the highlight text color."""
        color = QColorDialog.getColor(self.highlight_color)
        if color.isValid() and color != self.highlight_color:
            self.highlight_color = color
            self.highlight_color_button.setStyleSheet(f"background-color: {color.name()}")
            self.settings_changed.emit(color)

    def select_highlight_border_color(self):
        """Open a color picker and update the highlight border color."""
        color = QColorDialog.getColor(self.highlight_border_color)
        if color.isValid() and color != self.highlight_border_color:
            self.highlight_border_color = color
            self.highlight_border_button.setStyleSheet(f"background-color: {color.name()}")
            self.settings_changed.emit(color)

    def get_settings(self) -> dict:
        """
        Generate and return the highlight style in ASS format.

        Returns:
            dict: Dictionary containing the highlight style string.
        """
        text_color = qcolor_to_ass(self.highlight_color)
        border_color = qcolor_to_ass(self.highlight_border_color)
        highlight_style = rf"{{\1c{text_color}\3c{border_color}}}"

        if self.fade_highlight_checkbox.isChecked():
            highlight_style = highlight_style[:-1] + r"\fad(50,50)}"

        return {
            "highlight_style": highlight_style
        }

    def set_settings(self, settings: dict):
        """
        Parse and apply settings from a highlight style dictionary.

        Args:
            settings (dict): Dictionary containing 'highlight_style' key.
        """
        highlight_style = settings.get("highlight_style", "")
        if not highlight_style:
            return

        # Extract \1c&HXXXXXX for text color
        if r"\1c&H" in highlight_style:
            start = highlight_style.find(r"\1c&H") + 5
            end = highlight_style.find(r"\3c", start)
            if end == -1:
                end = highlight_style.find("}", start)
            color_str = highlight_style[start:end].strip("\\")
            self.highlight_color = ass_to_qcolor(f"&H{color_str}")
            self.highlight_color_button.setStyleSheet(f"background-color: {self.highlight_color.name()}")

        # Extract \3c&HXXXXXX for border color
        if r"\3c&H" in highlight_style:
            start = highlight_style.find(r"\3c&H") + 5
            end = highlight_style.find(r"\\", start)
            if end == -1:
                end = highlight_style.find("}", start)
            color_str = highlight_style[start:end].strip("\\")
            self.highlight_border_color = ass_to_qcolor(f"&H{color_str}")
            self.highlight_border_button.setStyleSheet(f"background-color: {self.highlight_border_color.name()}")

        # Determine if fading is used
        self.fade_highlight_checkbox.setChecked(r"\fad(" in highlight_style)
