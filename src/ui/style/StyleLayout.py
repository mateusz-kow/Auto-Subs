from typing import Any

from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from src.managers.style_manager import StyleManager

from .FontStyleLayout import FontStyleLayout
from .HighlightStyleLayout import HighlightStyleLayout


class StyleLayout(QScrollArea):
    """
    A layout that combines font and highlight styling controls
    and allows applying those styles via StyleManager.
    """

    def __init__(self, style_manager: StyleManager) -> None:
        super().__init__()

        # Create a container widget for the scrollable content
        container = QWidget()
        self.main_layout = QVBoxLayout(container)

        self.style_manager = style_manager

        style = style_manager.style
        self.font_layout = FontStyleLayout(style)
        self.highlight_layout = HighlightStyleLayout(style)

        self.main_layout.addLayout(self.font_layout)
        self.main_layout.addLayout(self.highlight_layout)

        self.font_layout.settings_changed.connect(self.apply_current_style)
        self.highlight_layout.settings_changed.connect(self.apply_current_style)

        # Set the container widget as the scrollable area
        self.setWidget(container)
        self.setWidgetResizable(True)

    def apply_current_style(self) -> None:
        """Collects current managers and applies them via StyleManager."""
        style_data = self.get_current_settings()
        self.style_manager.from_dict(style_data)

    def get_current_settings(self) -> dict[str, Any]:
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

    def on_style_loaded(self, new_style: dict[str, Any]) -> None:
        """
        Callback for when a new style is loaded.

        Args:
            new_style (dict): The loaded style data.

        """
        self.font_layout.set_settings(new_style)
        self.highlight_layout.set_settings(new_style)
