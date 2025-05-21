from PySide6.QtWidgets import QGraphicsRectItem
from src.ui.timeline.constants import *
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QMouseEvent, QPen

SELECTED_SEGMENT_COLOR = Qt.GlobalColor.green
FRAME_RATE = 60


class SegmentGraphic(QGraphicsRectItem):
    """Represents a single subtitle segment."""
    def __init__(self, segment, index):
        super().__init__()
        self.segment = segment
        self.index = index
        self.setRect(QRectF(segment.start * TIME_SCALE_FACTOR, SUBTITLE_BAR_Y,
                            (segment.end - segment.start) * TIME_SCALE_FACTOR, SUBTITLE_BAR_HEIGHT))
        self.setBrush(QBrush(SUBTITLE_BAR_COLOR))
        self.setToolTip(f"{segment.start:.2f}s - {segment.end:.2f}s: {str(segment)}")
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)  # Ensure selectable
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable, True)  # Ensure focusable

    def select(self):
        """Change the color to indicate selection."""
        self.setBrush(QBrush(SELECTED_SEGMENT_COLOR))

    def deselect(self):
        """Revert the color to the default."""
        self.setBrush(QBrush(SUBTITLE_BAR_COLOR))


class VideoGraphic(QGraphicsRectItem):
    """Represents the video bar with an interactive progress indicator."""

    def __init__(self, video_duration: float):
        super().__init__()
        self.total_frames = int(video_duration * FRAME_RATE)
        self.video_duration = video_duration
        self.current_frame = 0
        self.is_dragging = False

        # Background rectangle
        self.setRect(QRectF(0, 0, video_duration * TIME_SCALE_FACTOR, BAR_HEIGHT))
        self.setBrush(QBrush(VIDEO_BAR_COLOR))
        self.setPen(QPen(Qt.PenStyle.NoPen))  # No border

        # Progress fill rectangle
        self.fill_item = QGraphicsRectItem(self)
        self.fill_item.setRect(QRectF(0, 0, 0, BAR_HEIGHT))  # Initially empty
        self.fill_item.setBrush(QBrush(Qt.GlobalColor.green))

        # Set position
        self.setPos(0, VIDEO_BAR_Y)

    def update_progress(self, frame):
        """Update the progress bar based on the current frame."""
        self.current_frame = max(0, min(frame, self.total_frames))  # Clamp frame within valid range
        progress_width = (self.current_frame / self.total_frames) * self.rect().width()
        self.fill_item.setRect(QRectF(0, 0, progress_width, BAR_HEIGHT))

    def keyPressEvent(self, event):
        """Handle key press events to move the progress bar."""
        if event.key() == Qt.Key.Key_Left:
            self.update_progress(self.current_frame - 1)  # Move one frame left
        elif event.key() == Qt.Key.Key_Right:
            self.update_progress(self.current_frame + 1)  # Move one frame right
        super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle single click and start dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self._update_frame_from_position(event.pos().x())  # Update progress immediately on click

    def mouseMoveEvent(self, event: QMouseEvent):
        """Update the progress bar while dragging."""
        if self.is_dragging:
            self._update_frame_from_position(event.pos().x())

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Stop dragging the progress bar."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

    def _update_frame_from_position(self, x_pos):
        """Calculate and update the frame based on the x position."""
        relative_x = max(0, min(x_pos, self.rect().width()))  # Clamp x within the bar width
        frame = int((relative_x / self.rect().width()) * self.total_frames)
        self.update_progress(frame)
        self._notify_frame_change(frame)  # Notify about the frame change

    def _notify_frame_change(self, frame):
        """Notify the video manager or player about the frame change."""
        print(f"Frame updated to: {frame}")  # Replace with actual video update logic
