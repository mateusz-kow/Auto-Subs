from PySide6.QtWidgets import (
    QVBoxLayout, QFontComboBox, QSpinBox, QCheckBox, QPushButton,
    QComboBox, QHBoxLayout, QLabel, QColorDialog, QDoubleSpinBox
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal
from src.utils.color_operations import ass_to_qcolor, qcolor_to_ass


def _create_labeled_row(label_text, widget):
    row = QHBoxLayout()
    row.addWidget(QLabel(label_text))
    row.addWidget(widget)
    return row


class FontStyleLayout(QVBoxLayout):
    settings_changed = Signal(object)

    def __init__(self, style: dict):
        super().__init__()

        self.color_buttons = {}

        # === Font family ===
        self.font_selector = QFontComboBox()
        self.font_selector.currentFontChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Font:", self.font_selector))

        # === Font size ===
        self.font_size = QSpinBox()
        self.font_size.setRange(6, 100)
        self.font_size.setValue(36)
        self.font_size.valueChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Size:", self.font_size))

        # === Font styles ===
        self.bold_checkbox = QCheckBox("Bold")
        self.bold_checkbox.stateChanged.connect(self.settings_changed.emit)
        self.addWidget(self.bold_checkbox)

        self.italic_checkbox = QCheckBox("Italic")
        self.italic_checkbox.stateChanged.connect(self.settings_changed.emit)
        self.addWidget(self.italic_checkbox)

        self.underline_checkbox = QCheckBox("Underline")
        self.underline_checkbox.stateChanged.connect(self.settings_changed.emit)
        self.addWidget(self.underline_checkbox)

        self.strikeout_checkbox = QCheckBox("Strikeout")
        self.strikeout_checkbox.stateChanged.connect(self.settings_changed.emit)
        self.addWidget(self.strikeout_checkbox)

        # === Color pickers ===
        for name in ["primary_color", "secondary_color", "outline_color", "back_color"]:
            btn = QPushButton(f"{name.replace('_', ' ').title()}")
            btn.clicked.connect(lambda _, n=name: self.select_color(n))
            self.color_buttons[name] = {"button": btn, "color": QColor("#ffffff")}
            self._update_color_button_style(name)
            self.addWidget(btn)

        # === Alignment ===
        self.alignment = QComboBox()
        self.alignment.addItems(["Left", "Center", "Right"])
        self.alignment.setCurrentIndex(1)
        self.alignment.currentIndexChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Alignment:", self.alignment))

        # === Margins ===
        self.margin_l = QSpinBox()
        self.margin_r = QSpinBox()
        self.margin_v = QSpinBox()
        for spinbox in (self.margin_l, self.margin_r, self.margin_v):
            spinbox.setRange(0, 1000)
            spinbox.valueChanged.connect(self.settings_changed.emit)

        self.addLayout(_create_labeled_row("Left margin:", self.margin_l))
        self.addLayout(_create_labeled_row("Right margin:", self.margin_r))
        self.addLayout(_create_labeled_row("Vertical margin:", self.margin_v))

        # === Border style ===
        self.border_style = QComboBox()
        self.border_style.addItems(["Outline", "Opaque Box"])
        self.border_style.currentIndexChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Border style:", self.border_style))

        # === Outline & Shadow ===
        self.outline = QSpinBox()
        self.outline.setRange(0, 20)
        self.outline.valueChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Outline:", self.outline))

        self.shadow = QSpinBox()
        self.shadow.setRange(0, 20)
        self.shadow.valueChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Shadow:", self.shadow))

        # === Scale X/Y ===
        self.scale_x = QSpinBox()
        self.scale_y = QSpinBox()
        for scale in (self.scale_x, self.scale_y):
            scale.setRange(10, 500)
            scale.setSuffix("%")
            scale.valueChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Scale X:", self.scale_x))
        self.addLayout(_create_labeled_row("Scale Y:", self.scale_y))

        # === Spacing ===
        self.spacing_spinbox = QDoubleSpinBox()
        self.spacing_spinbox.setRange(-10.0, 10.0)
        self.spacing_spinbox.setDecimals(2)
        self.spacing_spinbox.setSingleStep(0.1)
        self.spacing_spinbox.valueChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Letter spacing:", self.spacing_spinbox))

        # === Angle ===
        self.angle = QSpinBox()
        self.angle.setRange(-360, 360)
        self.angle.valueChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Rotation (Angle):", self.angle))

        # === Encoding ===
        self.encoding = QComboBox()
        self.encoding.addItems(["ANSI", "UTF-8", "Unicode"])
        self.encoding.currentIndexChanged.connect(self.settings_changed.emit)
        self.addLayout(_create_labeled_row("Encoding:", self.encoding))

        self.set_settings(style)

    def _update_color_button_style(self, name):
        color = self.color_buttons[name]["color"]
        self.color_buttons[name]["button"].setStyleSheet(f"background-color: {color.name()}")

    def select_color(self, name):
        color = QColorDialog.getColor(self.color_buttons[name]["color"])
        if color.isValid():
            self.color_buttons[name]["color"] = color
            self._update_color_button_style(name)
            self.settings_changed.emit(self.get_settings())

    def get_settings(self):
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
            "alignment": self.alignment.currentIndex() + 1,
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

    def set_settings(self, settings: dict):
        self.font_selector.setCurrentText(settings["font"])
        self.font_size.setValue(settings["font_size"])
        self.bold_checkbox.setChecked(settings["bold"] == -1)
        self.italic_checkbox.setChecked(settings["italic"] == 1)
        self.underline_checkbox.setChecked(settings.get("underline", 0) == 1)
        self.strikeout_checkbox.setChecked(settings.get("strikeout", 0) == 1)

        for name in ["primary_color", "secondary_color", "outline_color", "back_color"]:
            self.color_buttons[name]["color"] = ass_to_qcolor(settings[name])
            self._update_color_button_style(name)

        self.alignment.setCurrentIndex(settings["alignment"] - 1)
        self.margin_l.setValue(settings["margin_l"])
        self.margin_r.setValue(settings["margin_r"])
        self.margin_v.setValue(settings["margin_v"])
        self.border_style.setCurrentIndex(0 if settings["border_style"] == 1 else 1)
        self.outline.setValue(settings["outline"])
        self.shadow.setValue(settings["shadow"])
        self.scale_x.setValue(settings.get("scale_x", 100))
        self.scale_y.setValue(settings.get("scale_y", 100))
        self.spacing_spinbox.setValue(settings.get("spacing_spinbox", 0.0))
        self.angle.setValue(settings.get("angle", 0))
        self.encoding.setCurrentIndex(settings["encoding"])
