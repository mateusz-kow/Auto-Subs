# src/ui/timeline/SegmentsBar.py
from logging import getLogger
from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QPoint, QPointF, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QPen, QWheelEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsTextItem, QGraphicsView, QMenu

from src.managers.subtitles_manager import SubtitlesManager
from src.managers.video_manager import VideoManager
from src.subtitles.models import Subtitles
from src.ui.timeline.constants import (
    MAJOR_MARKER_HEIGHT,
    MAJOR_MARKER_INTERVAL,
    MARKER_TEXT_OFFSET,
    MARKER_Y,
    MINOR_MARKER_HEIGHT,
    MINOR_MARKER_INTERVAL,
    SCENE_MIN_WIDTH,
    SUBTITLE_BAR_HEIGHT,
    SUBTITLE_BAR_Y,
    TIME_SCALE_FACTOR,
)
from src.ui.timeline.SubtitleSegmentBar import SubtitleSegmentBar
from src.ui.timeline.VideoSegmentBar import VideoSegmentBar

logger = getLogger(__name__)


class SegmentsBar(QGraphicsView):
    """
    Graphical timeline view displaying subtitle segments and the video progress bar.

    This view supports segment selection, preview synchronization, and context menu actions
    such as deletion or merging of subtitle segments. It is designed to be vertically
    expandable while keeping its content at a fixed height.

    Signals:
        segment_clicked (int): Emitted when a segment is clicked, with its index.
    """

    segment_clicked = Signal(int)

    def __init__(self, subtitles_manager: SubtitlesManager, video_manager: VideoManager) -> None:
        """
        Initialize the SegmentsBar.

        Args:
            subtitles_manager: Manages subtitle segment data.
            video_manager: Manages video metadata and playback state.
        """
        super().__init__()

        self.subtitles_manager = subtitles_manager
        self.video_manager = video_manager
        self.selected_segments: set[int] = set()
        self.preview_time_listeners: list[Callable[[float], Any]] = []

        # Graphics scene setup
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._step = 0
        self._subtitles: Subtitles | None = subtitles_manager.subtitles
        self._video_duration = 0.0

        logger.debug("SegmentsBar initialized")

    def handle_segment_click(self, segment_item: SubtitleSegmentBar, event: QGraphicsSceneMouseEvent) -> None:
        """
        Handle mouse click on a subtitle segment.

        Args:
            segment_item (SubtitleSegmentBar): The clicked segment.
            event (QMouseEvent): The mouse event.
        """
        logger.debug("Segment clicked (index=%d, modifiers=%s)", segment_item.index, event.modifiers())
        self.segment_clicked.emit(segment_item.index)

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._toggle_segment_selection(segment_item)
        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            self._select_range(segment_item)
        else:
            self.clear_selection()
            self._select_segment(segment_item)

    def update_timeline(self, subtitles: Subtitles | None, video_duration: float) -> None:
        """
        Refresh the entire timeline with new subtitle and video data.

        Args:
            subtitles: Subtitle data structure with segments.
            video_duration (float): Duration of the video in seconds.
        """
        segment_count = len(subtitles.segments) if subtitles and subtitles.segments else 0
        logger.info(
            "Updating timeline (segments=%d, duration=%.2f)",
            segment_count,
            video_duration,
        )

        self._scene.clear()
        self.setUpdatesEnabled(False)

        self._step = 0
        self._subtitles = subtitles
        self._video_duration = video_duration

        QTimer.singleShot(0, self._step_update)

    def _step_update(self) -> None:
        """Incremental, staged update of the timeline UI to avoid blocking the main thread."""
        try:
            if self._step == 0:
                self._add_time_markers(self._video_duration)

            elif self._step == 1:
                self._add_video_bar(self._video_duration)

            elif self._step == 2:
                if self._subtitles and self._subtitles.segments:
                    for i, segment in enumerate(self._subtitles.segments):
                        segment_item = SubtitleSegmentBar(segment, i, self)
                        self._scene.addItem(segment_item)

            elif self._step == 3:
                total_duration = max(
                    self._video_duration,
                    self._subtitles.segments[-1].end if self._subtitles and self._subtitles.segments else 0,
                )
                scene_width = max(SCENE_MIN_WIDTH, int(total_duration * TIME_SCALE_FACTOR))
                scene_height = SUBTITLE_BAR_Y + SUBTITLE_BAR_HEIGHT + 5  # Ensure scene is tall enough for content
                self._scene.setSceneRect(0, 0, scene_width, scene_height)

                self.setUpdatesEnabled(True)
                logger.info("Timeline update complete")
                return  # Exit the loop

            self._step += 1
            QTimer.singleShot(0, self._step_update)

        except Exception as e:
            logger.exception("Error during timeline update step %d: %s", self._step, e)

    def _add_video_bar(self, video_duration: float) -> None:
        """Add the video playback bar to the timeline."""
        if video_duration > 0:
            video_bar = VideoSegmentBar(video_duration, self)
            self._scene.addItem(video_bar)

    def _add_time_markers(self, video_duration: float) -> None:
        """Add visual time markers to the timeline based on video duration."""
        for sec in range(0, int(video_duration) + 1, MINOR_MARKER_INTERVAL):
            x_pos = sec * TIME_SCALE_FACTOR
            is_major = sec % MAJOR_MARKER_INTERVAL == 0
            height = MAJOR_MARKER_HEIGHT if is_major else MINOR_MARKER_HEIGHT

            self._scene.addLine(x_pos, MARKER_Y, x_pos, MARKER_Y + height, QPen(Qt.GlobalColor.white, 1))

            if is_major:
                text = QGraphicsTextItem(f"{sec}s")
                text.setDefaultTextColor(Qt.GlobalColor.white)
                text.setPos(QPointF(x_pos - MARKER_TEXT_OFFSET / 2, MARKER_Y + height + 2))
                self._scene.addItem(text)

    def _select_segment(self, segment_item: SubtitleSegmentBar) -> None:
        logger.debug("Selecting segment %d", segment_item.index)
        self.selected_segments.add(segment_item.index)
        segment_item.select()

    def _toggle_segment_selection(self, segment_item: SubtitleSegmentBar) -> None:
        if segment_item.index in self.selected_segments:
            logger.debug("Deselecting segment %d", segment_item.index)
            self.selected_segments.remove(segment_item.index)
            segment_item.deselect()
        else:
            logger.debug("Adding segment to selection %d", segment_item.index)
            self.selected_segments.add(segment_item.index)
            segment_item.select()

    def _select_range(self, segment_item: SubtitleSegmentBar) -> None:
        if not self.selected_segments:
            self._select_segment(segment_item)
            return

        last_selected = max(self.selected_segments)
        start, end = sorted((last_selected, segment_item.index))
        logger.debug("Selecting range: %d to %d", start, end)

        for item in self._scene.items():
            if isinstance(item, SubtitleSegmentBar) and start <= item.index <= end:
                self.selected_segments.add(item.index)
                item.select()

    def clear_selection(self) -> None:
        """Deselect all currently selected subtitle segments."""
        logger.debug("Clearing all segment selections")
        for item in self._scene.items():
            if isinstance(item, SubtitleSegmentBar):
                item.deselect()
        self.selected_segments.clear()

    def show_context_menu(self, position: QPoint) -> None:
        """
        Show context menu for subtitle segment actions.

        Args:
            position: Screen position for context menu display.
        """
        if not self.selected_segments:
            return

        logger.debug("Showing context menu at %s", position)
        menu = QMenu(self)
        delete_action = QAction("Delete Segments", self)
        merge_action = QAction("Merge Segments", self)

        delete_action.triggered.connect(self.delete_segments)
        merge_action.triggered.connect(self.merge_segments)

        menu.addAction(delete_action)
        menu.addAction(merge_action)
        menu.exec(position)

    def delete_segments(self) -> None:
        """Request deletion of all currently selected subtitle segments."""
        logger.info("Deleting %d selected segments", len(self.selected_segments))
        self.subtitles_manager.delete_segments(self.selected_segments)

    def merge_segments(self) -> None:
        """Request merging of all currently selected subtitle segments."""
        logger.info("Merging %d selected segments", len(self.selected_segments))
        self.subtitles_manager.merge_segments(self.selected_segments)

    def request_segment_resize(self, segment_index: int, new_start: float, new_end: float) -> None:
        """Request a resize operation from the SubtitlesManager."""
        logger.info("Requesting resize for segment %d to start: %.2f, end: %.2f", segment_index, new_start, new_end)
        self.subtitles_manager.resize_segment(segment_index, new_start, new_end)

    def get_resize_boundaries(self, segment_index: int) -> tuple[float, float]:
        """
        Get the valid resize boundaries for a segment to prevent overlap.

        Returns:
            A tuple (left_boundary, right_boundary) in seconds.
        """
        if not self.subtitles_manager.subtitles:
            return 0.0, self.video_manager.video_duration

        segments = self.subtitles_manager.subtitles.segments
        # Left boundary is the end time of the previous segment, or 0.0
        left_boundary = segments[segment_index - 1].end if segment_index > 0 else 0.0
        # Right boundary is the start time of the next segment, or video duration
        right_boundary = (
            segments[segment_index + 1].start
            if segment_index < len(segments) - 1
            else self.video_manager.video_duration
        )
        return left_boundary, right_boundary

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Enable horizontal scrolling using the mouse wheel."""
        delta = event.angleDelta().y()
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)

    def notify_preview_time_change(self, timestamp: float) -> None:
        """
        Notify registered listeners that the preview time has changed.

        Args:
            timestamp (float): New preview timestamp in seconds.
        """
        logger.debug("Preview time changed: %.2f seconds", timestamp)
        for listener in self.preview_time_listeners:
            listener(timestamp)

    def add_preview_time_listener(self, listener: Callable[[float], Any]) -> None:
        """
        Add a listener for preview time updates.

        Args:
            listener (Callable): Function to call with updated timestamp.
        """
        if listener not in self.preview_time_listeners:
            self.preview_time_listeners.append(listener)
            logger.debug("Preview time listener added: %s", listener)
        else:
            logger.warning("Listener already registered: %s", listener)

    def on_subtitles_changed(self, subtitles: Subtitles) -> None:
        """
        Callback for subtitle data changes.

        Args:
            subtitles: New subtitle data to display.
        """
        logger.info("Subtitles changed (%d segments)", len(subtitles.segments) if subtitles else 0)
        self.clear_selection()
        self.update_timeline(subtitles, self.video_manager.video_duration)

    def on_video_changed(self, video_path: Path) -> None:
        """
        Callback for video source changes.

        Args:
            video_path (str): Path to the new video file.
        """
        logger.info("Video changed: %s", video_path)
        self.clear_selection()
        self.update_timeline(self.subtitles_manager.subtitles, self.video_manager.video_duration)
