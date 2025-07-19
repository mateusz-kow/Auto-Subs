from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsSceneHoverEvent, QGraphicsSceneMouseEvent

from src.subtitles.models import SubtitleSegment
from src.ui.timeline.constants import (
    SELECTED_SEGMENT_COLOR,
    SUBTITLE_BAR_COLOR,
    SUBTITLE_BAR_HEIGHT,
    SUBTITLE_BAR_Y,
    TIME_SCALE_FACTOR,
)

if TYPE_CHECKING:
    from src.ui.timeline.segments_bar import SegmentsBar


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
        self._parent_controller: SegmentsBar = parent_controller

        self._is_resizing = False
        self._resize_handle: str | None = None
        self._resize_margin = 5
        self._min_duration_px = 0.0

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
        self.setAcceptHoverEvents(True)

    def select(self) -> None:
        """Visually indicate that the segment is selected."""
        self.setBrush(QBrush(SELECTED_SEGMENT_COLOR))

    def deselect(self) -> None:
        """Revert the visual state to indicate the segment is not selected."""
        self.setBrush(QBrush(SUBTITLE_BAR_COLOR))

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """Change cursor shape when hovering over resizable edges."""
        pos = event.pos()
        rect = self.rect()

        on_left_edge = abs(pos.x() - rect.left()) < self._resize_margin
        on_right_edge = abs(pos.x() - rect.right()) < self._resize_margin

        if on_left_edge or on_right_edge:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """Reset cursor when leaving the item."""
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle mouse press events for interaction."""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            rect = self.rect()

            on_left_edge = abs(pos.x() - rect.left()) < self._resize_margin
            on_right_edge = abs(pos.x() - rect.right()) < self._resize_margin

            if on_left_edge or on_right_edge:
                self._is_resizing = True
                self._resize_handle = "left" if on_left_edge else "right"

                segment_data = self._parent_controller.subtitles_manager.subtitles.segments[self._index]
                min_duration_s = len(segment_data.words) * 0.05
                self._min_duration_px = min_duration_s * TIME_SCALE_FACTOR

                event.accept()
                return

            self._parent_controller.handle_segment_click(self, event)
        else:
            self._parent_controller.show_context_menu(event.screenPos())

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Handle dragging for resize."""
        if not self._is_resizing:
            super().mouseMoveEvent(event)
            return

        rect = self.rect()
        new_pos_x = event.pos().x()
        left_boundary_px, right_boundary_px = self._get_boundaries_in_pixels()
        new_rect: QRectF

        if self._resize_handle == "left":
            clamped_x = max(left_boundary_px, min(new_pos_x, rect.right() - self._min_duration_px))
            new_rect = QRectF(clamped_x, rect.y(), rect.right() - clamped_x, rect.height())
        elif self._resize_handle == "right":
            clamped_x = max(rect.left() + self._min_duration_px, min(new_pos_x, right_boundary_px))
            new_rect = QRectF(rect.x(), rect.y(), clamped_x - rect.x(), rect.height())
        else:
            super().mouseMoveEvent(event)
            return

        self.setRect(new_rect)
        event.accept()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Finalize resize on mouse release."""
        if self._is_resizing and event.button() == Qt.MouseButton.LeftButton:
            self._is_resizing = False
            self._resize_handle = None
            self.setCursor(Qt.CursorShape.ArrowCursor)

            final_rect = self.rect()
            new_start = final_rect.left() / TIME_SCALE_FACTOR
            new_end = final_rect.right() / TIME_SCALE_FACTOR

            self._parent_controller.request_segment_resize(self._index, new_start, new_end)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def _get_boundaries_in_pixels(self) -> tuple[float, float]:
        """Get resize boundaries in scene pixel coordinates."""
        left_s, right_s = self._parent_controller.get_resize_boundaries(self._index)
        return left_s * TIME_SCALE_FACTOR, right_s * TIME_SCALE_FACTOR

    @property
    def index(self) -> int:
        return self._index
