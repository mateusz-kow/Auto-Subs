from logging import getLogger

from PySide6.QtCore import QPointF, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QMouseEvent, QPen, QWheelEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsView, QMenu

from src.ui.timeline.constants import (
    BAR_HEIGHT,
    MAJOR_MARKER_HEIGHT,
    MAJOR_MARKER_INTERVAL,
    MARKER_TEXT_OFFSET,
    MARKER_Y,
    MINOR_MARKER_HEIGHT,
    MINOR_MARKER_INTERVAL,
    SCENE_MIN_WIDTH,
    SUBTITLE_BAR_HEIGHT,
    TIME_SCALE_FACTOR,
    VIDEO_BAR_Y,
)
from src.ui.timeline.SubtitleSegmentBar import SubtitleSegmentBar
from src.ui.timeline.VideoSegmentBar import VideoSegmentBar

logger = getLogger(__name__)


class SegmentsBar(QGraphicsView):
    """
    Graphical timeline view displaying subtitle segments and the video progress bar.

    This view supports segment selection, preview synchronization, and context menu actions
    such as deletion or merging of subtitle segments.

    Signals:
        segment_clicked (int): Emitted when a segment is clicked, with its index.
    """

    segment_clicked = Signal(int)

    def __init__(self, subtitles_manager, video_manager):
        """
        Initialize the SegmentsBar.

        Args:
            subtitles_manager: Manages subtitle segment data.
            video_manager: Manages video metadata and playback state.
        """
        super().__init__()

        self.subtitles_manager = subtitles_manager
        self.video_manager = video_manager
        self.selected_segments = set()
        self.preview_time_listeners = []

        # Graphics scene setup
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setFixedHeight(SUBTITLE_BAR_HEIGHT + BAR_HEIGHT + VIDEO_BAR_Y)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Register data change listeners
        self.video_manager.add_video_listener(self.on_video_changed)
        self.subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)

        self._step = 0
        self._subtitles = None
        self._video_duration = 0

        logger.debug("SegmentsBar initialized")

    def handle_segment_click(self, segment_item: SubtitleSegmentBar, event: QMouseEvent):
        """
        Handle mouse click on a subtitle segment.

        Args:
            segment_item (SubtitleSegmentBar): The clicked segment.
            event (QMouseEvent): The mouse event.
        """
        logger.debug("Segment clicked (index=%d, modifiers=%s)", segment_item._index, event.modifiers())
        self.segment_clicked.emit(segment_item._index)

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._toggle_segment_selection(segment_item)
        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            self._select_range(segment_item)
        else:
            self.clear_selection()
            self._select_segment(segment_item)

    def update_timeline(self, subtitles, video_duration: float):
        """
        Refresh the entire timeline with new subtitle and video data.

        Args:
            subtitles: Subtitle data structure with segments.
            video_duration (float): Duration of the video in seconds.
        """
        logger.info(
            "Updating timeline (segments=%d, duration=%.2f)",
            len(subtitles.segments) if subtitles and subtitles.segments else 0,
            video_duration,
        )

        self.scene.clear()
        self.setUpdatesEnabled(False)

        self._step = 0
        self._subtitles = subtitles
        self._video_duration = video_duration

        QTimer.singleShot(0, self._step_update)

    def _step_update(self):
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
                        self.scene.addItem(segment_item)

            elif self._step == 3:
                total_duration = max(
                    self._video_duration,
                    self._subtitles.segments[-1].end if self._subtitles and self._subtitles.segments else 0,
                )
                scene_width = max(SCENE_MIN_WIDTH, int(total_duration * TIME_SCALE_FACTOR))
                self.scene.setSceneRect(0, 0, scene_width, self.height())
                self.setUpdatesEnabled(True)
                logger.info("Timeline update complete")
                return  # Exit the loop

            self._step += 1
            QTimer.singleShot(0, self._step_update)

        except Exception as e:
            logger.exception("Error during timeline update step %d: %s", self._step, e)

    def _add_video_bar(self, video_duration: float):
        """Add the video playback bar to the timeline."""
        video_bar = VideoSegmentBar(video_duration, self)
        self.scene.addItem(video_bar)

    def _add_time_markers(self, video_duration: float):
        """Add visual time markers to the timeline based on video duration."""
        for sec in range(0, int(video_duration) + 1, MINOR_MARKER_INTERVAL):
            x_pos = sec * TIME_SCALE_FACTOR
            is_major = sec % MAJOR_MARKER_INTERVAL == 0
            height = MAJOR_MARKER_HEIGHT if is_major else MINOR_MARKER_HEIGHT

            self.scene.addLine(x_pos, MARKER_Y, x_pos, MARKER_Y + height, QPen(Qt.GlobalColor.white, 1))

            if is_major:
                text = QGraphicsTextItem(f"{sec}s")
                text.setDefaultTextColor(Qt.GlobalColor.white)
                text.setPos(QPointF(x_pos - MARKER_TEXT_OFFSET / 2, MARKER_Y + height + 2))
                self.scene.addItem(text)

    def _select_segment(self, segment_item: SubtitleSegmentBar):
        logger.debug("Selecting segment %d", segment_item._index)
        self.selected_segments.add(segment_item._index)
        segment_item.select()

    def _toggle_segment_selection(self, segment_item: SubtitleSegmentBar):
        if segment_item._index in self.selected_segments:
            logger.debug("Deselecting segment %d", segment_item._index)
            self.selected_segments.remove(segment_item._index)
            segment_item.deselect()
        else:
            logger.debug("Adding segment to selection %d", segment_item._index)
            self.selected_segments.add(segment_item._index)
            segment_item.select()

    def _select_range(self, segment_item: SubtitleSegmentBar):
        if not self.selected_segments:
            self._select_segment(segment_item)
            return

        last_selected = max(self.selected_segments)
        start, end = sorted((last_selected, segment_item._index))
        logger.debug("Selecting range: %d to %d", start, end)

        for item in self.scene.items():
            if isinstance(item, SubtitleSegmentBar) and start <= item._index <= end:
                self.selected_segments.add(item._index)
                item.select()

    def clear_selection(self):
        """Deselect all currently selected subtitle segments."""
        logger.debug("Clearing all segment selections")
        for item in self.scene.items():
            if isinstance(item, SubtitleSegmentBar):
                item.deselect()
        self.selected_segments.clear()

    def show_context_menu(self, position):
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

    def delete_segments(self):
        """Request deletion of all currently selected subtitle segments."""
        logger.info("Deleting %d selected segments", len(self.selected_segments))
        self.subtitles_manager.delete_segments(self.selected_segments)

    def merge_segments(self):
        """Request merging of all currently selected subtitle segments."""
        logger.info("Merging %d selected segments", len(self.selected_segments))
        self.subtitles_manager.merge_segments(self.selected_segments)

    def wheelEvent(self, event: QWheelEvent):
        """Enable horizontal scrolling using the mouse wheel."""
        delta = event.angleDelta().y()
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)

    def notify_preview_time_change(self, timestamp: float):
        """
        Notify registered listeners that the preview time has changed.

        Args:
            timestamp (float): New preview timestamp in seconds.
        """
        logger.debug("Preview time changed: %.2f seconds", timestamp)
        for listener in self.preview_time_listeners:
            listener(timestamp)

    def add_preview_time_listener(self, listener):
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

    def on_subtitles_changed(self, subtitles):
        """
        Callback for subtitle data changes.

        Args:
            subtitles: New subtitle data to display.
        """
        logger.info("Subtitles changed (%d segments)", len(subtitles.segments) if subtitles else 0)
        self.clear_selection()
        video_duration = getattr(self.video_manager, "_video_duration", 0)
        self.update_timeline(subtitles, video_duration)

    def on_video_changed(self, video_path: str):
        """
        Callback for video source changes.

        Args:
            video_path (str): Path to the new video file.
        """
        logger.info("Video changed: %s", video_path)
        self.clear_selection()
        video_duration = getattr(self.video_manager, "_video_duration", 0)
        subtitles = getattr(self.subtitles_manager, "_subtitles", None)
        self.update_timeline(subtitles, video_duration)
