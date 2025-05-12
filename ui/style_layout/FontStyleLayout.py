from PySide6.QtWidgets import (
    QVBoxLayout, QFontComboBox, QSpinBox, QCheckBox, QPushButton,
    QComboBox, QHBoxLayout, QLabel, QColorDialog
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal


def _create_labeled_row(label_text, widget):
    row = QHBoxLayout()
    row.addWidget(QLabel(label_text))
    row.addWidget(widget)
    return row


class FontStyleLayout(QVBoxLayout):
    """
    Layout providing UI controls for configuring font-related subtitle styles,
    such as font family, size, color, margins, borders, and encoding.

    Emits:
        settings_changed: Signal emitted whenever a user changes a font-related setting.
    """

    settings_changed = Signal(object)

    def __init__(self):
        super().__init__()

        # Font family selector
        self.font_selector = QFontComboBox()
        self.font_selector.currentFontChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Font:", self.font_selector))

        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(6, 100)
        self.font_size.setValue(55)
        self.font_size.valueChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Size:", self.font_size))

        # Bold/Italic checkboxes
        self.bold_checkbox = QCheckBox("Bold")
        self.bold_checkbox.setChecked(True)
        self.bold_checkbox.stateChanged.connect(self.settings_changed.emit)
        self.addWidget(self.bold_checkbox)

        self.italic_checkbox = QCheckBox("Italic")
        self.italic_checkbox.stateChanged.connect(self.settings_changed.emit)
        self.addWidget(self.italic_checkbox)

        # Text color button
        self.color_button = QPushButton("Text color")
        self.selected_color_qcolor = QColor("#ffffff")
        self._update_color_button_style()
        self.color_button.clicked.connect(self.select_color)
        self.addWidget(self.color_button)

        # Alignment dropdown
        self.alignment = QComboBox()
        self.alignment.addItems(["Left", "Center", "Right"])
        self.alignment.setCurrentIndex(1)
        self.alignment.currentIndexChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Alignment:", self.alignment))

        # Margins
        self.margin_l = QSpinBox()
        self.margin_r = QSpinBox()
        self.margin_v = QSpinBox()
        for spinbox in (self.margin_l, self.margin_r, self.margin_v):
            spinbox.setRange(0, 1000)
            spinbox.valueChanged.connect(self.settings_changed.emit)

        self.margin_l.setValue(10)
        self.margin_r.setValue(10)
        self.margin_v.setValue(500)
        self.addLayout(_create_labeled_row("Left margin:", self.margin_l))
        self.addLayout(_create_labeled_row("Right margin:", self.margin_r))
        self.addLayout(_create_labeled_row("Vertical margin:", self.margin_v))

        # Border style
        self.border_style = QComboBox()
        self.border_style.addItems(["Outline", "Opaque Box"])
        self.border_style.setCurrentIndex(0)
        self.border_style.currentIndexChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Border style:", self.border_style))

        # Outline and shadow
        self.outline = QSpinBox()
        self.outline.setRange(0, 20)
        self.outline.setValue(8)
        self.outline.valueChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Outline:", self.outline))

        self.shadow = QSpinBox()
        self.shadow.setRange(0, 20)
        self.shadow.setValue(0)
        self.shadow.valueChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Shadow:", self.shadow))

        # Encoding
        self.encoding = QComboBox()
        self.encoding.addItems(["ANSI", "UTF-8", "Unicode"])
        self.encoding.setCurrentIndex(0)
        self.encoding.currentIndexChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Encoding:", self.encoding))

    def _update_color_button_style(self):
        self.color_button.setStyleSheet(f"background-color: {self.selected_color_qcolor.name()}")

    def select_color(self):
        """Open a color dialog to select the text color."""
        color = QColorDialog.getColor(self.selected_color_qcolor)
        if color.isValid() and color != self.selected_color_qcolor:
            self.selected_color_qcolor = color
            self._update_color_button_style()
            self.settings_changed.emit(color)

    def get_settings(self):
        """Return the current font-related style settings as a dictionary."""
        rgb = self.selected_color_qcolor.rgb() & 0xFFFFFF
        bgr_hex = f'{(rgb & 0xFF):02X}{(rgb >> 8 & 0xFF):02X}{(rgb >> 16 & 0xFF):02X}'
        primary_color = f"&H00{bgr_hex}"

        return {
            "font": self.font_selector.currentText(),
            "font_size": self.font_size.value(),
            "bold": -1 if self.bold_checkbox.isChecked() else 0,
            "italic": 1 if self.italic_checkbox.isChecked() else 0,
            "primary_color": primary_color,
            "alignment": self.alignment.currentIndex() + 1,
            "margin_l": self.margin_l.value(),
            "margin_r": self.margin_r.value(),
            "margin_v": self.margin_v.value(),
            "border_style": 1 if self.border_style.currentIndex() == 0 else 3,
            "outline": self.outline.value(),
            "shadow": self.shadow.value(),
            "encoding": self.encoding.currentIndex()
        }

    def set_settings(self, settings: dict):
        """Apply style settings from a dictionary."""
        def from_ass_color(ass_color: str) -> QColor:
            bgr = ass_color[2:] if ass_color.startswith("&H") else ass_color
            r = int(bgr[4:6], 16)
            g = int(bgr[2:4], 16)
            b = int(bgr[0:2], 16)
            return QColor(r, g, b)

        self.font_selector.setCurrentText(settings["font"])
        self.font_size.setValue(settings["font_size"])
        self.bold_checkbox.setChecked(settings["bold"] == -1)
        self.italic_checkbox.setChecked(settings["italic"] == 1)

        self.selected_color_qcolor = from_ass_color(settings["primary_color"])
        self._update_color_button_style()

        self.alignment.setCurrentIndex(settings["alignment"] - 1)
        self.margin_l.setValue(settings["margin_l"])
        self.margin_r.setValue(settings["margin_r"])
        self.margin_v.setValue(settings["margin_v"])
        self.border_style.setCurrentIndex(0 if settings["border_style"] == 1 else 1)
        self.outline.setValue(settings["outline"])
        self.shadow.setValue(settings["shadow"])
        self.encoding.setCurrentIndex(settings["encoding"])
