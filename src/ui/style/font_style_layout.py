from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFontComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.utils.operations.color_operations import ass_to_qcolor, qcolor_to_ass


def _create_labeled_row(label_text: str, widget: QWidget) -> QHBoxLayout:
    """Utility function to create a horizontal layout row with a label and widget.

    Args:
        label_text (str): Text for the QLabel.
        widget (QWidget): Widget to place next to the label.

    Returns:
        QHBoxLayout: The completed layout row.
    """
    row = QHBoxLayout()
    row.addWidget(QLabel(label_text))
    row.addWidget(widget)
    return row


class FontStyleLayout(QVBoxLayout):
    """A layout that provides user controls for configuring subtitle font styles.

    Emits:
        settings_changed (dict): Signal emitted whenever the style configuration is updated.
    """

    settings_changed = Signal(object)

    def __init__(self, style: dict[str, Any]):
        """Initialize the font style layout with given style settings.

        Args:
            style (dict): A dictionary containing font style configuration.
        """
        super().__init__()
        self._block_signals = False
        self.color_buttons: dict[str, dict[str, Any]] = {}

        self.font_selector = QFontComboBox()
        self.font_selector.currentFontChanged.connect(self._emit_settings)
        self.addLayout(_create_labeled_row("Font:", self.font_selector))

        self.font_size = QSpinBox()
        self.font_size.setRange(6, 100)
        self.font_size.setValue(36)
        self.font_size.valueChanged.connect(self._emit_settings)
        self.addLayout(_create_labeled_row("Size:", self.font_size))

        # Font style checkboxes
        self.bold_checkbox = QCheckBox("Bold")
        self.bold_checkbox.stateChanged.connect(self._emit_settings)
        self.addWidget(self.bold_checkbox)

        self.italic_checkbox = QCheckBox("Italic")
        self.italic_checkbox.stateChanged.connect(self._emit_settings)
        self.addWidget(self.italic_checkbox)

        self.underline_checkbox = QCheckBox("Underline")
        self.underline_checkbox.stateChanged.connect(self._emit_settings)
        self.addWidget(self.underline_checkbox)

        self.strikeout_checkbox = QCheckBox("Strikeout")
        self.strikeout_checkbox.stateChanged.connect(self._emit_settings)
        self.addWidget(self.strikeout_checkbox)

        # Color selection buttons
        for name in ["primary_color", "secondary_color", "outline_color", "back_color"]:
            btn = QPushButton(name.replace("_", " ").title())
            btn.clicked.connect(lambda _, n=name: self._select_color(n))
            self.color_buttons[name] = {"button": btn, "color": QColor("#ffffff")}
            self._update_color_button_style(name)
            self.addWidget(btn)

        self._alignment = QComboBox()
        self._alignment.addItems(["Left", "Center", "Right"])
        self._alignment.setCurrentIndex(1)
        self._alignment.currentIndexChanged.connect(self._emit_settings)
        self.addLayout(_create_labeled_row("Alignment:", self._alignment))

        # Margin spinboxes
        self.margin_l = QSpinBox()
        self.margin_r = QSpinBox()
        self.margin_v = QSpinBox()
        for label, box in [
            ("Left margin:", self.margin_l),
            ("Right margin:", self.margin_r),
            ("Vertical margin:", self.margin_v),
        ]:
            box.setRange(0, 1000)
            box.valueChanged.connect(self._emit_settings)
            self.addLayout(_create_labeled_row(label, box))

        self.border_style = QComboBox()
        self.border_style.addItems(["Outline", "Opaque Box"])
        self.border_style.currentIndexChanged.connect(self._emit_settings)
        self.addLayout(_create_labeled_row("Border style:", self.border_style))

        self.outline = QSpinBox()
        self.outline.setRange(0, 20)
        self.outline.valueChanged.connect(self._emit_settings)
        self.addLayout(_create_labeled_row("Outline:", self.outline))

        self.shadow = QSpinBox()
        self.shadow.setRange(0, 20)
        self.shadow.valueChanged.connect(self._emit_settings)
        self.addLayout(_create_labeled_row("Shadow:", self.shadow))

        self.scale_x = QSpinBox()
        self.scale_y = QSpinBox()
        for label, box in [("Scale X:", self.scale_x), ("Scale Y:", self.scale_y)]:
            box.setRange(10, 500)
            box.setSuffix("%")
            box.valueChanged.connect(self._emit_settings)
            self.addLayout(_create_labeled_row(label, box))

        self.spacing_spinbox = QDoubleSpinBox()
        self.spacing_spinbox.setRange(-10.0, 10.0)
        self.spacing_spinbox.setDecimals(2)
        self.spacing_spinbox.setSingleStep(0.1)
        self.spacing_spinbox.valueChanged.connect(self._emit_settings)
        self.addLayout(_create_labeled_row("Letter spacing:", self.spacing_spinbox))

        self.angle = QSpinBox()
        self.angle.setRange(-360, 360)
        self.angle.valueChanged.connect(self._emit_settings)
        self.addLayout(_create_labeled_row("Rotation (Angle):", self.angle))

        self.encoding = QComboBox()
        self.encoding.addItems(["ANSI", "UTF-8", "Unicode"])
        self.encoding.currentIndexChanged.connect(self._emit_settings)
        self.addLayout(_create_labeled_row("Encoding:", self.encoding))

        self.set_settings(style)

    def _update_color_button_style(self, name: str) -> None:
        """Update the background color of a color picker button.

        Args:
            name (str): The name of the color field (e.g., "primary_color").
        """
        color: QColor = self.color_buttons[name]["color"]
        button: QPushButton = self.color_buttons[name]["button"]
        button.setStyleSheet(f"background-color: {color.name()}")

    def _select_color(self, name: str) -> None:
        """Open a QColorDialog for selecting a new color.

        Args:
            name (str): The color field to update (e.g., "back_color").
        """
        current: QColor = self.color_buttons[name]["color"]
        color = QColorDialog.getColor(current)
        if color.isValid():
            self.color_buttons[name]["color"] = color
            self._update_color_button_style(name)
            self._emit_settings()

    def _emit_settings(self) -> None:
        """Emit the settings_changed signal with the current settings."""
        if self._block_signals:
            return
        self.settings_changed.emit(self.get_settings())

    def get_settings(self) -> dict[str, Any]:
        """Retrieve the current font style configuration.

        Returns:
            dict: The current font style settings.
        """
        return {
            "font": self.font_selector.currentText(),
            "font_size": self.font_size.value(),
            "bold": -1 if self.bold_checkbox.isChecked() else 0,
            "italic": 1 if self.italic_checkbox.isChecked() else 0,
            "underline": 1 if self.underline_checkbox.isChecked() else 0,
            "strikeout": 1 if self.strikeout_checkbox.isChecked() else 0,
            "primary_color": qcolor_to_ass(self.color_buttons["primary_color"]["color"]),
            "secondary_color": qcolor_to_ass(self.color_buttons["secondary_color"]["color"]),
            "outline_color": qcolor_to_ass(self.color_buttons["outline_color"]["color"]),
            "back_color": qcolor_to_ass(self.color_buttons["back_color"]["color"]),
            "alignment": self._alignment.currentIndex() + 1,
            "margin_l": self.margin_l.value(),
            "margin_r": self.margin_r.value(),
            "margin_v": self.margin_v.value(),
            "border_style": 1 if self.border_style.currentIndex() == 0 else 3,
            "outline": self.outline.value(),
            "shadow": self.shadow.value(),
            "scale_x": self.scale_x.value(),
            "scale_y": self.scale_y.value(),
            "spacing_spinbox": self.spacing_spinbox.value(),
            "angle": self.angle.value(),
            "encoding": self.encoding.currentIndex(),
        }

    def set_settings(self, settings: dict[str, Any]) -> None:
        """Apply a font style configuration from a dictionary.

        Args:
            settings (dict): Font style configuration to apply.
        """
        self._block_signals = True
        try:
            self.font_selector.setCurrentText(settings.get("font", "Arial"))
            self.font_size.setValue(settings.get("font_size", 36))
            self.bold_checkbox.setChecked(settings.get("bold", 0) == -1)
            self.italic_checkbox.setChecked(settings.get("italic", 0) == 1)
            self.underline_checkbox.setChecked(settings.get("underline", 0) == 1)
            self.strikeout_checkbox.setChecked(settings.get("strikeout", 0) == 1)

            for name in self.color_buttons:
                color = ass_to_qcolor(settings.get(name, "&H00FFFFFF"))
                self.color_buttons[name]["color"] = color
                self._update_color_button_style(name)

            self._alignment.setCurrentIndex(max(0, settings.get("alignment", 2) - 1))
            self.margin_l.setValue(settings.get("margin_l", 10))
            self.margin_r.setValue(settings.get("margin_r", 10))
            self.margin_v.setValue(settings.get("margin_v", 10))
            self.border_style.setCurrentIndex(0 if settings.get("border_style", 1) == 1 else 1)
            self.outline.setValue(settings.get("outline", 1))
            self.shadow.setValue(settings.get("shadow", 0))
            self.scale_x.setValue(settings.get("scale_x", 100))
            self.scale_y.setValue(settings.get("scale_y", 100))
            self.spacing_spinbox.setValue(settings.get("spacing_spinbox", 0.0))
            self.angle.setValue(settings.get("angle", 0))
            self.encoding.setCurrentIndex(settings.get("encoding", 0))
        finally:
            self._block_signals = False
