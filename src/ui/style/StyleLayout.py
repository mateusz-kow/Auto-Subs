from PySide6.QtWidgets import QVBoxLayout, QLabel, QSlider, QScrollArea, QWidget
from PySide6.QtCore import Qt
import warnings

from src.managers.StyleManager import StyleManager
from .FontStyleLayout import FontStyleLayout
from .HighlightStyleLayout import HighlightStyleLayout


class StyleLayout(QScrollArea):
    """
    A layout that combines font and highlight styling controls
    and allows applying those styles via StyleManager.
    """

    def __init__(self, style_manager: StyleManager):
        super().__init__()

        # Create a container widget for the scrollable content
        container = QWidget()
        self.layout = QVBoxLayout(container)

        self.style_manager = style_manager

        style = style_manager.style
        self.font_layout = FontStyleLayout(style)
        self.highlight_layout = HighlightStyleLayout(style)

        self.layout.addLayout(self.font_layout)
        self.layout.addLayout(self.highlight_layout)

        self.font_layout.settings_changed.connect(self.apply_current_style)
        self.highlight_layout.settings_changed.connect(self.apply_current_style)

        # Subscribe to style loaded events
        style_manager.add_style_loaded_listener(self.on_style_loaded)

        # Set the container widget as the scrollable area
        self.setWidget(container)
        self.setWidgetResizable(True)

    def apply_current_style(self):
        """
        Collects current managers and applies them via StyleManager.
        """

        style_data = self.get_current_settings()
        self.style_manager.from_dict(style_data)

    def get_current_settings(self):
        """
        Combines font and highlight managers into a single dictionary.

        Returns:
            dict: Combined style managers.
        """
        return {
            "title": "Default",
            **self.font_layout.get_settings(),
            **self.highlight_layout.get_settings(),
        }

    def on_style_loaded(self, new_style: dict):
        """
        Callback for when a new style is loaded.

        Args:
            new_style (dict): The loaded style data.

        """
        self.font_layout.set_settings(new_style)
        self.highlight_layout.set_settings(new_style)
