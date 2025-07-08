from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QCheckBox, QColorDialog, QPushButton, QVBoxLayout

from src.utils.color_operations import ass_to_qcolor, qcolor_to_ass


class HighlightStyleLayout(QVBoxLayout):
    """
    A layout providing controls to configure subtitle highlight styles using a structured dictionary.

    Users can customize:
        - Highlight text color
        - Highlight border color
        - Whether to fade the highlight in/out

    Emits:
        settings_changed (dict): Emitted when the user modifies any setting.
    """

    settings_changed = Signal(object)

    def __init__(self, style: dict):
        """
        Initialize the highlight style configuration UI.

        Args:
            style (dict): Initial style dictionary to load.
        """
        super().__init__()

        # Default values
        self.highlight_color = QColor("#ffcc99")
        self.highlight_border_color = QColor("#000000")

        # Highlight color button
        self.highlight_color_button = QPushButton("Highlight Color (Text)")
        self.highlight_color_button.setStyleSheet(f"background-color: {self.highlight_color.name()}")
        self.highlight_color_button.clicked.connect(self._select_highlight_color)
        self.addWidget(self.highlight_color_button)

        # Border color button
        self.highlight_border_button = QPushButton("Highlight Color (Border)")
        self.highlight_border_button.setStyleSheet(f"background-color: {self.highlight_border_color.name()}")
        self.highlight_border_button.clicked.connect(self._select_highlight_border_color)
        self.addWidget(self.highlight_border_button)

        # Fade toggle
        self.fade_highlight_checkbox = QCheckBox("Fade Highlight In/Out")
        self.fade_highlight_checkbox.stateChanged.connect(lambda _: self._emit_settings())
        self.addWidget(self.fade_highlight_checkbox)

        # Load initial settings
        self.set_settings(style)

    def _select_highlight_color(self):
        """Open a color picker for the text highlight color."""
        color = QColorDialog.getColor(self.highlight_color)
        if color.isValid() and color != self.highlight_color:
            self.highlight_color = color
            self.highlight_color_button.setStyleSheet(f"background-color: {color.name()}")
            self._emit_settings()

    def _select_highlight_border_color(self):
        """Open a color picker for the border highlight color."""
        color = QColorDialog.getColor(self.highlight_border_color)
        if color.isValid() and color != self.highlight_border_color:
            self.highlight_border_color = color
            self.highlight_border_button.setStyleSheet(f"background-color: {color.name()}")
            self._emit_settings()

    def _emit_settings(self):
        """Emit the current settings dictionary to listeners."""
        self.settings_changed.emit(self.get_settings())

    def get_settings(self) -> dict:
        """
        Retrieve the current highlight style as a dictionary.

        Returns:
            dict: A dictionary with keys `text_color`, `border_color`, and `fade`.
        """
        return {
            "highlight_style": {
                "text_color": qcolor_to_ass(self.highlight_color),
                "border_color": qcolor_to_ass(self.highlight_border_color),
                "fade": self.fade_highlight_checkbox.isChecked(),
            }
        }

    def set_settings(self, settings: dict):
        """
        Apply highlight style settings from a dictionary.

        Args:
            settings (dict): A dictionary containing highlight style configuration.
        """
        style = settings.get("highlight_style", {})

        # Set text highlight color
        if "text_color" in style:
            color = ass_to_qcolor(style["text_color"])
            if color.isValid():
                self.highlight_color = color
                self.highlight_color_button.setStyleSheet(f"background-color: {color.name()}")

        # Set border highlight color
        if "border_color" in style:
            color = ass_to_qcolor(style["border_color"])
            if color.isValid():
                self.highlight_border_color = color
                self.highlight_border_button.setStyleSheet(f"background-color: {color.name()}")

        # Set fade toggle
        self.fade_highlight_checkbox.setChecked(bool(style.get("fade", False)))
