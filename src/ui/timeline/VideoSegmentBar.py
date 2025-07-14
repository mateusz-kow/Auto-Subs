from logging import getLogger
from typing import Any

from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QKeyEvent, QPen, Qt
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsSceneMouseEvent

from src.ui.timeline.constants import (
    BAR_HEIGHT,
    FRAME_RATE,
    TIME_SCALE_FACTOR,
    VIDEO_BAR_COLOR,
    VIDEO_BAR_Y,
)

logger = getLogger(__name__)


class VideoSegmentBar(QGraphicsRectItem):
    """
    Represents the video timeline bar with an interactive progress indicator.

    This class handles visual representation of video progress,
    mouse-based seeking, and keyboard interaction for frame-wise navigation.

    Attributes:
        total_frames (int): Total number of frames in the video.
        video_duration (float): Duration of the video in seconds.
        current_frame (int): The current frame displayed in the progress bar.
        is_dragging (bool): Indicates whether the user is currently dragging the progress bar.
        parent_controller: Reference to the controller handling playback logic.
        fill_item (QGraphicsRectItem): The graphical fill representing playback progress.
    """

    def __init__(self, video_duration: float, parent_controller: Any) -> None:
        """
        Initialize the VideoSegmentBar.

        Args:
            video_duration (float): Total duration of the video in seconds.
            parent_controller: Controller managing interactions and time updates.
        """
        super().__init__()

        self.video_duration: float = video_duration
        self.total_frames: int = int(video_duration * FRAME_RATE)
        self.current_frame: int = 0
        self.is_dragging: bool = False
        self.parent_controller: Any = parent_controller

        # Set up the video bar background
        self.setRect(QRectF(0, 0, video_duration * TIME_SCALE_FACTOR, BAR_HEIGHT))
        self.setBrush(QBrush(VIDEO_BAR_COLOR))
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setPos(0, VIDEO_BAR_Y)

        # Progress fill item
        self.fill_item: QGraphicsRectItem = QGraphicsRectItem(self)
        self.fill_item.setRect(QRectF(0, 0, 0, BAR_HEIGHT))
        self.fill_item.setBrush(QBrush(Qt.GlobalColor.green))

        logger.info("VideoSegmentBar initialized with duration: %.2f seconds", video_duration)

    def update_progress(self, frame: int) -> None:
        """
        Update the visual progress of the bar to the specified frame.

        Args:
            frame (int): The current frame to represent.
        """
        self.current_frame = max(0, min(frame, self.total_frames))  # Clamp to valid range
        width = (self.current_frame / self.total_frames) * self.rect().width()
        self.fill_item.setRect(QRectF(0, 0, width, BAR_HEIGHT))
        logger.debug("Progress updated to frame %d (%.2f seconds)", frame, frame / FRAME_RATE)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handle keyboard events to navigate frames.

        Args:
            event (QKeyEvent): The key press event (e.g., left/right arrow).
        """
        if event.key() == Qt.Key.Key_Left:
            self.update_progress(self.current_frame - 1)
        elif event.key() == Qt.Key.Key_Right:
            self.update_progress(self.current_frame + 1)
        super().keyPressEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """
        Start dragging and update progress on mouse press.

        Args:
            event (QGraphicsSceneMouseEvent): The mouse press event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self._update_progress_from_position(event.pos().x())
            logger.info("Mouse press detected. Dragging started.")

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """
        Update progress while dragging the mouse.

        Args:
            event (QGraphicsSceneMouseEvent): The mouse move event.
        """
        if self.is_dragging:
            self._update_progress_from_position(event.pos().x())
            logger.debug("Dragging... Updated progress from mouse move.")

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """
        Stop dragging on mouse release.

        Args:
            event (QGraphicsSceneMouseEvent): The mouse release event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            logger.info("Mouse released. Dragging ended.")

    def _update_progress_from_position(self, x_pos: float) -> None:
        """
        Convert x-coordinate to frame number and update progress.

        Args:
            x_pos (float): The horizontal position of the cursor within the bar.
        """
        bar_width = self.rect().width()
        clamped_x = max(0.0, min(x_pos, bar_width))
        frame = int((clamped_x / bar_width) * self.total_frames)
        self.update_progress(frame)
        self._notify_preview_time_change(frame / FRAME_RATE)

    def _notify_preview_time_change(self, timestamp: float) -> None:
        """
        Notify the parent controller that the preview time has changed.

        Args:
            timestamp (float): The current timestamp in seconds.
        """
        if hasattr(self.parent_controller, "notify_preview_time_change"):
            self.parent_controller.notify_preview_time_change(timestamp)
            logger.info("Preview time updated to: %.2f seconds", timestamp)
