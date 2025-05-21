from PySide6.QtWidgets import QGraphicsRectItem
from src.ui.timeline.constants import *
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QMouseEvent


class SubtitleSegmentBar(QGraphicsRectItem):
    """Represents a single subtitle segment."""

    def __init__(self, segment, index: int, parent_controller):
        super().__init__()
        self.segment = segment
        self.index = index
        self.parent_controller = parent_controller  # Reference to the parent controller
        self.setRect(QRectF(segment.start * TIME_SCALE_FACTOR, SUBTITLE_BAR_Y,
                            (segment.end - segment.start) * TIME_SCALE_FACTOR, SUBTITLE_BAR_HEIGHT))
        self.setBrush(QBrush(SUBTITLE_BAR_COLOR))
        self.setToolTip(f"{segment.start:.2f}s - {segment.end:.2f}s: {str(segment)}")
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable, True)

    def select(self):
        """Change the color to indicate selection."""
        self.setBrush(QBrush(SELECTED_SEGMENT_COLOR))

    def deselect(self):
        """Revert the color to the default."""
        self.setBrush(QBrush(SUBTITLE_BAR_COLOR))

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse clicks for selection."""
        if event.button() == Qt.MouseButton.LeftButton:
            modifiers = event.modifiers()
            self.parent_controller.handle_segment_click(self, modifiers)
        else:
            self.parent_controller.show_context_menu(event.screenPos())
