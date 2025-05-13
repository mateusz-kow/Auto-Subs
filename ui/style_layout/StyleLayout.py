import warnings

from PySide6.QtWidgets import QVBoxLayout, QLabel

from src.settings.StyleManager import StyleManager
from .FontStyleLayout import FontStyleLayout
from .HighlightStyleLayout import HighlightStyleLayout


class StyleLayout(QVBoxLayout):
    """
    A layout that combines font and highlight styling controls
    and allows applying those styles via StyleManager.
    """

    def __init__(self):
        super().__init__()

        self.addWidget(QLabel("Subtitle Styling"))

        self.font_layout = FontStyleLayout()
        self.highlight_layout = HighlightStyleLayout()

        self.addLayout(self.font_layout)
        self.addLayout(self.highlight_layout)

        self.font_layout.settings_changed.connect(self.apply_current_style)
        self.highlight_layout.settings_changed.connect(self.apply_current_style)

        # Subscribe to style loaded events
        StyleManager().add_style_loaded_listener(self.on_style_loaded)

    def apply_current_style(self):
        """
        Collects current settings and applies them via StyleManager.
        """
        warnings.warn("TODO: Consider adding debounce or throttling here.")

        style_data = self.get_current_settings()
        StyleManager().from_dict(style_data)

    def get_current_settings(self):
        """
        Combines font and highlight settings into a single dictionary.

        Returns:
            dict: Combined style settings.
        """
        return {
            "title": "Default",
            **self.font_layout.get_settings(),
            **self.highlight_layout.get_settings()
        }

    def on_style_loaded(self, new_style: dict):
        """
        Callback for when a new style is loaded.

        Args:
            new_style (dict): The loaded style data.

        """
        self.font_layout.set_settings(new_style)
        self.highlight_layout.set_settings(new_style)
