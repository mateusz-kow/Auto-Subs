from logging import getLogger

from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QMouseEvent, QPen
from PySide6.QtWidgets import QGraphicsRectItem

from src.ui.timeline.constants import *

logger = getLogger(__name__)


class VideoSegmentBar(QGraphicsRectItem):
    """Represents the video bar with an interactive progress indicator."""

    def __init__(self, video_duration: float, parent_controller):
        """
        Initialize the VideoBar.

        Args:
            video_duration (float): The total duration of the video in seconds.
            parent_controller: The parent controller managing this VideoBar.
        """
        super().__init__()
        self.total_frames = int(video_duration * FRAME_RATE)
        self.video_duration = video_duration
        self.current_frame = 0
        self.is_dragging = False
        self.parent_controller = parent_controller  # Reference to the parent controller

        # Configure the background rectangle
        self.setRect(QRectF(0, 0, video_duration * TIME_SCALE_FACTOR, BAR_HEIGHT))
        self.setBrush(QBrush(VIDEO_BAR_COLOR))
        self.setPen(QPen(Qt.PenStyle.NoPen))  # No border

        # Configure the progress fill rectangle
        self.fill_item = QGraphicsRectItem(self)
        self.fill_item.setRect(QRectF(0, 0, 0, BAR_HEIGHT))  # Initially empty
        self.fill_item.setBrush(QBrush(Qt.GlobalColor.green))

        # Set the position of the video bar
        self.setPos(0, VIDEO_BAR_Y)

        logger.info("VideoBar initialized with duration: %.2f seconds", video_duration)

    def update_progress(self, frame: int) -> None:
        """
        Update the progress bar based on the current frame.

        Args:
            frame (int): The current frame to update the progress to.
        """
        self.current_frame = max(0, min(frame, self.total_frames))  # Clamp frame within valid range
        progress_width = (self.current_frame / self.total_frames) * self.rect().width()
        self.fill_item.setRect(QRectF(0, 0, progress_width, BAR_HEIGHT))
        logger.debug("Progress updated to frame: %d (%.2f seconds)", frame, frame / FRAME_RATE)

    def keyPressEvent(self, event) -> None:
        """
        Handle key press events to move the progress bar.

        Args:
            event: The key press event.
        """
        if event.key() == Qt.Key.Key_Left:
            self.update_progress(self.current_frame - 1)  # Move one frame left
        elif event.key() == Qt.Key.Key_Right:
            self.update_progress(self.current_frame + 1)  # Move one frame right
        super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse press events to start dragging or update progress.

        Args:
            event (QMouseEvent): The mouse press event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self._update_progress_from_position(event.pos().x())  # Update progress immediately on click
            logger.info("Mouse press detected. Dragging started.")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse move events to update the progress bar while dragging.

        Args:
            event (QMouseEvent): The mouse move event.
        """
        if self.is_dragging:
            self._update_progress_from_position(event.pos().x())
            logger.debug("Mouse moved. Dragging in progress.")

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handle mouse release events to stop dragging.

        Args:
            event (QMouseEvent): The mouse release event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            logger.info("Mouse released. Dragging stopped.")

    def _update_progress_from_position(self, x_pos: float) -> None:
        """
        Calculate and update the progress based on the x position.

        Args:
            x_pos (float): The x-coordinate of the mouse position relative to the bar.
        """
        relative_x = max(0, min(x_pos, self.rect().width()))  # Clamp x within the bar width
        frame = int((relative_x / self.rect().width()) * self.total_frames)
        self.update_progress(frame)
        self._notify_preview_time_change(frame / FRAME_RATE)  # Notify about the time change

    def _notify_preview_time_change(self, timestamp: float) -> None:
        """
        Notify the parent controller about the time change.

        Args:
            timestamp (float): The current timestamp in seconds.
        """
        if hasattr(self.parent_controller, "notify_preview_time_change"):
            self.parent_controller.notify_preview_time_change(timestamp)
            logger.info("Preview time updated to: %.2f seconds", timestamp)
