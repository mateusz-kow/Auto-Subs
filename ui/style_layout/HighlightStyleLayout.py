from PySide6.QtWidgets import QVBoxLayout, QPushButton, QCheckBox, QColorDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal


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
        def to_ass_color(qcolor: QColor) -> str:
            rgb = qcolor.rgb() & 0xFFFFFF
            bgr_hex = f'{(rgb & 0xFF):02X}{(rgb >> 8 & 0xFF):02X}{(rgb >> 16 & 0xFF):02X}'
            return f"&H{bgr_hex}"

        text_color = to_ass_color(self.highlight_color)
        border_color = to_ass_color(self.highlight_border_color)
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
        def from_ass_color(ass_color: str) -> QColor:
            # Convert &HBBGGRR to QColor(R, G, B)
            hex_part = ass_color[2:] if ass_color.startswith("&H") else ass_color
            r = int(hex_part[4:6], 16)
            g = int(hex_part[2:4], 16)
            b = int(hex_part[0:2], 16)
            return QColor(r, g, b)

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
            self.highlight_color = from_ass_color(f"&H{color_str}")
            self.highlight_color_button.setStyleSheet(f"background-color: {self.highlight_color.name()}")

        # Extract \3c&HXXXXXX for border color
        if r"\3c&H" in highlight_style:
            start = highlight_style.find(r"\3c&H") + 5
            end = highlight_style.find(r"\\", start)
            if end == -1:
                end = highlight_style.find("}", start)
            color_str = highlight_style[start:end].strip("\\")
            self.highlight_border_color = from_ass_color(f"&H{color_str}")
            self.highlight_border_button.setStyleSheet(f"background-color: {self.highlight_border_color.name()}")

        # Determine if fading is used
        self.fade_highlight_checkbox.setChecked(r"\fad(" in highlight_style)
