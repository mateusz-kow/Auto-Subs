from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QPen, Qt
from PySide6.QtWidgets import QGraphicsRectItem

from src.ui.timeline.constants import (
    BAR_HEIGHT,
    TIME_SCALE_FACTOR,
    VIDEO_BAR_COLOR,
    VIDEO_BAR_Y,
)

if TYPE_CHECKING:
    from src.ui.timeline.segments_bar import SegmentsBar

logger = getLogger(__name__)


class VideoSegmentBar(QGraphicsRectItem):
    """Represents the visual background bar for the video's total duration."""

    def __init__(self, video_duration: float, parent_controller: SegmentsBar) -> None:
        """Initialize the VideoSegmentBar.

        Args:
            video_duration (float): Total duration of the video in seconds.
            parent_controller: Controller managing interactions and time updates.
        """
        super().__init__()

        self.video_duration: float = video_duration
        self.parent_controller: SegmentsBar = parent_controller

        # Set up the video bar background
        self.setRect(QRectF(0, 0, video_duration * TIME_SCALE_FACTOR, BAR_HEIGHT))
        self.setBrush(QBrush(VIDEO_BAR_COLOR))
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setPos(0, VIDEO_BAR_Y)

        logger.info("VideoSegmentBar initialized with duration: %.2f seconds", video_duration)
