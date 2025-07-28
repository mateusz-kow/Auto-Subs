from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFontComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLayout,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.utils.operations.color_operations import ass_to_qcolor, qcolor_to_ass


class _CollapsibleBox(QWidget):
    """A custom widget that provides a collapsible group box."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        """Initialize the _CollapsibleBox."""
        super().__init__(parent)

        self.toggle_button = QToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setStyleSheet(
            """
            QToolButton {
                border: none;
                font-weight: bold;
                padding: 5px;
                text-align: left;
            }
            QToolButton:hover {
                background-color: #80808033;
            }
        """
        )

        self.content_area = QFrame()
        self.content_area.setFrameShape(QFrame.Shape.NoFrame)
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_area)

        self.toggle_button.toggled.connect(self._on_toggled)

        # Set initial state to expanded (open) by default
        self.toggle_button.setChecked(True)

    def _on_toggled(self, checked: bool) -> None:
        """Handle toggling the collapsible box.

        Args:
            checked: True if the box is expanded, False if collapsed.
        """
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)
        self.content_area.setVisible(checked)

    def set_content_layout(self, layout: QLayout) -> None:
        """Set the layout for the content area."""
        old_layout = self.content_area.layout()
        if old_layout is not None:
            QWidget().setLayout(old_layout)
        self.content_area.setLayout(layout)


class FontStyleLayout(QWidget):
    """A widget that provides user controls for configuring subtitle font styles,
    organized into collapsible sections.
    """

    settings_changed = Signal(object)

    def __init__(self, style: dict[str, Any]) -> None:
        """Initialize the font style layout with given style settings.

        Args:
            style (dict): A dictionary containing font style configuration.
        """
        super().__init__()
        self._block_signals = False
        self.color_buttons: dict[str, dict[str, Any]] = {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # --- Font & Text Section ---
        font_section = _CollapsibleBox("Font & Text")
        font_layout = QFormLayout()
        self.font_selector = QFontComboBox()
        font_layout.addRow("Font:", self.font_selector)
        self.font_size = QSpinBox()
        self.font_size.setRange(6, 100)
        font_layout.addRow("Size:", self.font_size)
        self.bold_checkbox = QCheckBox("Bold")
        self.italic_checkbox = QCheckBox("Italic")
        self.underline_checkbox = QCheckBox("Underline")
        self.strikeout_checkbox = QCheckBox("Strikeout")
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.bold_checkbox)
        checkbox_layout.addWidget(self.italic_checkbox)
        checkbox_layout.addWidget(self.underline_checkbox)
        checkbox_layout.addWidget(self.strikeout_checkbox)
        checkbox_layout.addStretch()
        font_layout.addRow(checkbox_layout)
        self.spacing_spinbox = QDoubleSpinBox()
        self.spacing_spinbox.setRange(-10.0, 10.0)
        self.spacing_spinbox.setDecimals(2)
        self.spacing_spinbox.setSingleStep(0.1)
        font_layout.addRow("Letter spacing:", self.spacing_spinbox)
        font_section.set_content_layout(font_layout)
        main_layout.addWidget(font_section)

        # --- Colors Section ---
        colors_section = _CollapsibleBox("Colors")
        colors_layout = QVBoxLayout()
        for name in ["primary_color", "secondary_color", "outline_color", "back_color"]:
            btn = QPushButton(name.replace("_", " ").title())
            btn.clicked.connect(lambda _, n=name: self._select_color(n))
            self.color_buttons[name] = {"button": btn, "color": QColor("#ffffff")}
            self._update_color_button_style(name)
            colors_layout.addWidget(btn)
        colors_section.set_content_layout(colors_layout)
        main_layout.addWidget(colors_section)

        # --- Positioning & Layout Section ---
        pos_section = _CollapsibleBox("Positioning & Layout")
        pos_layout = QFormLayout()
        self._alignment = QComboBox()
        self._alignment.addItems(["Left", "Center", "Right"])
        pos_layout.addRow("Alignment:", self._alignment)
        self.margin_l = QSpinBox()
        self.margin_r = QSpinBox()
        self.margin_v = QSpinBox()
        for box in (self.margin_l, self.margin_r, self.margin_v):
            box.setRange(0, 1000)
        pos_layout.addRow("Left margin:", self.margin_l)
        pos_layout.addRow("Right margin:", self.margin_r)
        pos_layout.addRow("Vertical margin:", self.margin_v)
        self.angle = QSpinBox()
        self.angle.setRange(-360, 360)
        pos_layout.addRow("Rotation (Angle):", self.angle)
        pos_section.set_content_layout(pos_layout)
        main_layout.addWidget(pos_section)

        # --- Border & Shadow Section ---
        border_section = _CollapsibleBox("Border & Shadow")
        border_layout = QFormLayout()
        self.border_style = QComboBox()
        self.border_style.addItems(["Outline", "Opaque Box"])
        border_layout.addRow("Border style:", self.border_style)
        self.outline = QSpinBox()
        self.outline.setRange(0, 20)
        border_layout.addRow("Outline:", self.outline)
        self.shadow = QSpinBox()
        self.shadow.setRange(0, 20)
        border_layout.addRow("Shadow:", self.shadow)
        border_section.set_content_layout(border_layout)
        main_layout.addWidget(border_section)

        # --- Advanced Section ---
        advanced_section = _CollapsibleBox("Advanced")
        advanced_layout = QFormLayout()
        self.scale_x = QSpinBox()
        self.scale_y = QSpinBox()
        for box in (self.scale_x, self.scale_y):
            box.setRange(10, 500)
            box.setSuffix("%")
        advanced_layout.addRow("Scale X:", self.scale_x)
        advanced_layout.addRow("Scale Y:", self.scale_y)
        self.encoding = QComboBox()
        self.encoding.addItems(["ANSI", "UTF-8", "Unicode"])
        advanced_layout.addRow("Encoding:", self.encoding)
        advanced_section.set_content_layout(advanced_layout)
        main_layout.addWidget(advanced_section)

        self._connect_signals()
        self.set_settings(style)

    def _connect_signals(self) -> None:
        """Connect all widget signals to the settings emitter."""
        widgets_to_connect = [
            self.font_selector,
            self.font_size,
            self.bold_checkbox,
            self.italic_checkbox,
            self.underline_checkbox,
            self.strikeout_checkbox,
            self._alignment,
            self.margin_l,
            self.margin_r,
            self.margin_v,
            self.border_style,
            self.outline,
            self.shadow,
            self.scale_x,
            self.scale_y,
            self.spacing_spinbox,
            self.angle,
            self.encoding,
        ]
        for widget in widgets_to_connect:
            if isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self._emit_settings)
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.valueChanged.connect(self._emit_settings)
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self._emit_settings)
            elif isinstance(widget, QFontComboBox):
                widget.currentFontChanged.connect(self._emit_settings)

    def _update_color_button_style(self, name: str) -> None:
        """Update the background color of a color picker button."""
        color: QColor = self.color_buttons[name]["color"]
        button: QPushButton = self.color_buttons[name]["button"]
        button.setStyleSheet(f"background-color: {color.name()}")

    def _select_color(self, name: str) -> None:
        """Open a QColorDialog for selecting a new color."""
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
        """Retrieve the current font style configuration."""
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
        """Apply a font style configuration from a dictionary."""
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
