from logging import getLogger

from PySide6.QtCore import QLineF
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QGraphicsLineItem

from src.ui.timeline.constants import SPECIAL_MARKER_COLOR, TIME_SCALE_FACTOR

logger = getLogger(__name__)


class TimelineIndicator(QGraphicsLineItem):
    """A vertical line that indicates the current playback position on the timeline."""

    def __init__(self, scene_height: float, parent: QGraphicsLineItem | None = None) -> None:
        """Initialize the TimelineIndicator.

        Args:
            scene_height (float): The total height of the scene to span.
            parent (QGraphicsLineItem, optional): The parent item. Defaults to None.
        """
        super().__init__(parent)
        self._scene_height = scene_height
        self.setLine(QLineF(0, 0, 0, self._scene_height))

        pen = QPen(SPECIAL_MARKER_COLOR)
        pen.setWidth(2)
        self.setPen(pen)
        self.setZValue(10)  # Ensure it's rendered on top of other items

    def set_position(self, time: float) -> None:
        """Set the horizontal position of the indicator based on a timestamp.

        Args:
            time (float): The time in seconds.
        """
        x_pos = time * TIME_SCALE_FACTOR
        self.setX(x_pos)
