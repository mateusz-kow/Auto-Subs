from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsSceneMouseEvent

from src.subtitles.models import SubtitleSegment
from src.ui.timeline.constants import (
    SELECTED_SEGMENT_COLOR,
    SUBTITLE_BAR_COLOR,
    SUBTITLE_BAR_HEIGHT,
    SUBTITLE_BAR_Y,
    TIME_SCALE_FACTOR,
)
from src.ui.timeline.SegmentsBar import SegmentsBar


class SubtitleSegmentBar(QGraphicsRectItem):
    """
    A graphical representation of a single subtitle segment in a timeline view.

    This item is responsible for displaying a colored bar that corresponds to a subtitle's
    start and end time. It also supports interaction such as selection and context menus.

    Attributes:
        _index (int): The position of the segment in the sequence.
        _parent_controller: A reference to the controller managing this item.
    """

    def __init__(self, segment: SubtitleSegment, index: int, parent_controller: SegmentsBar) -> None:
        """
        Initialize the subtitle segment bar.

        Args:
            segment: An object containing `start` and `end` time properties.
            index (int): Index of the segment in the subtitle list.
            parent_controller: Reference to the controller managing this segment.
        """
        super().__init__()
        self._index = index
        self._parent_controller = parent_controller  # Reference to the parent controller

        # Set the size and position of the subtitle segment
        self.setRect(
            QRectF(
                segment.start * TIME_SCALE_FACTOR,
                SUBTITLE_BAR_Y,
                (segment.end - segment.start) * TIME_SCALE_FACTOR,
                SUBTITLE_BAR_HEIGHT,
            )
        )
        self.setBrush(QBrush(SUBTITLE_BAR_COLOR))
        self.setToolTip(f"{segment.start:.2f}s - {segment.end:.2f}s: {str(segment)}")

        # Enable interactivity
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable, True)

    def select(self) -> None:
        """Visually indicate that the segment is selected."""
        self.setBrush(QBrush(SELECTED_SEGMENT_COLOR))

    def deselect(self) -> None:
        """Revert the visual state to indicate the segment is not selected."""
        self.setBrush(QBrush(SUBTITLE_BAR_COLOR))

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """
        Handle mouse press events for interaction.

        Args:
            event (QMouseEvent): The mouse event instance.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._parent_controller.handle_segment_click(self, event)
        else:
            self._parent_controller.show_context_menu(event.screenPos())

    @property
    def index(self) -> int:
        return self._index
