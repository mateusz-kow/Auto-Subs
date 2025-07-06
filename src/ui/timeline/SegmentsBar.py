from PySide6.QtGui import QAction, QPen, QWheelEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsTextItem, QMenu
from PySide6.QtCore import QPointF, QTimer, Qt

from src.ui.timeline.VideoSegmentBar import VideoSegmentBar
from src.ui.timeline.SubtitleSegmentBar import SubtitleSegmentBar
from src.ui.timeline.constants import *
from logging import getLogger

logger = getLogger(__name__)


class SegmentsBar(QGraphicsView):
    def __init__(self, subtitles_manager, video_manager):
        super().__init__()

        self.subtitles_manager = subtitles_manager
        self.video_manager = video_manager
        self.selected_segments = set()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFixedHeight(SUBTITLE_BAR_HEIGHT + BAR_HEIGHT + VIDEO_BAR_Y)
        self.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.preview_time_listeners = []

        # Connect listeners
        self.video_manager.add_video_listener(self.on_video_changed)
        self.subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)

        self._add_time_markers(30)
        logger.debug("SegmentsBar initialized")

    def update_timeline(self, subtitles, video_duration):
        logger.info(
            "Updating timeline (subtitles=%d segments, duration=%.2f)",
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
        try:
            if self._step == 0:
                logger.debug("Step 0: Adding time markers")
                self._add_time_markers(self._video_duration)
            elif self._step == 1:
                logger.debug("Step 1: Adding video bar")
                self._add_video_bar(self._video_duration)
            elif self._step == 2:
                logger.debug("Step 2: Adding subtitle segments")
                if self._subtitles and self._subtitles.segments:
                    for i, segment in enumerate(self._subtitles.segments):
                        segment_item = SubtitleSegmentBar(segment, i, self)
                        self.scene.addItem(segment_item)
            elif self._step == 3:
                logger.debug("Step 3: Adjusting scene rect and enabling updates")
                total_duration = max(
                    self._video_duration,
                    (
                        self._subtitles.segments[-1].end
                        if self._subtitles and self._subtitles.segments
                        else 0
                    ),
                )
                scene_width = max(
                    SCENE_MIN_WIDTH, int(total_duration * TIME_SCALE_FACTOR)
                )
                self.scene.setSceneRect(0, 0, scene_width, self.height())
                self.setUpdatesEnabled(True)
                logger.info("Timeline update complete")
                return  # Do not continue calling singleShot

            self._step += 1
            QTimer.singleShot(0, self._step_update)
        except Exception as e:
            logger.exception("Error during timeline update step %d: %s", self._step, e)

    def _add_video_bar(self, video_duration):
        video_bar = VideoSegmentBar(video_duration, self)
        self.scene.addItem(video_bar)

    def _add_time_markers(self, video_duration):
        for sec in range(0, int(video_duration) + 1, MINOR_MARKER_INTERVAL):
            x_pos = sec * TIME_SCALE_FACTOR
            is_major = sec % MAJOR_MARKER_INTERVAL == 0
            line_height = MAJOR_MARKER_HEIGHT if is_major else MINOR_MARKER_HEIGHT
            pen = QPen(Qt.GlobalColor.white, 1)
            self.scene.addLine(x_pos, MARKER_Y, x_pos, MARKER_Y + line_height, pen)

            if is_major:
                marker_text = QGraphicsTextItem(f"{sec}s")
                marker_text.setDefaultTextColor(Qt.GlobalColor.white)
                marker_text.setPos(
                    QPointF(x_pos - MARKER_TEXT_OFFSET / 2, MARKER_Y + line_height + 2)
                )
                self.scene.addItem(marker_text)

    def handle_segment_click(self, segment_item, modifiers):
        logger.debug(
            "Segment clicked (index=%d, modifiers=%s)", segment_item.index, modifiers
        )
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            self._toggle_segment_selection(segment_item)
        elif modifiers == Qt.KeyboardModifier.ShiftModifier:
            self._select_range(segment_item)
        else:
            self.clear_selection()
            self._select_segment(segment_item)

    def _select_segment(self, segment_item):
        logger.debug("Selecting segment %d", segment_item.index)
        self.selected_segments.add(segment_item.index)
        segment_item.select()

    def _toggle_segment_selection(self, segment_item):
        if segment_item.index in self.selected_segments:
            logger.debug("Deselecting segment %d", segment_item.index)
            self.selected_segments.remove(segment_item.index)
            segment_item.deselect()
        else:
            logger.debug("Selecting additional segment %d", segment_item.index)
            self.selected_segments.add(segment_item.index)
            segment_item.select()

    def _select_range(self, segment_item):
        if not self.selected_segments:
            logger.debug("Range selection: no previous selection, selecting current")
            self._select_segment(segment_item)
            return

        last_selected = max(self.selected_segments)
        start = min(last_selected, segment_item.index)
        end = max(last_selected, segment_item.index)
        logger.debug("Selecting range: %d to %d", start, end)

        for item in self.scene.items():
            if isinstance(item, SubtitleSegmentBar) and start <= item.index <= end:
                self.selected_segments.add(item.index)
                item.select()

    def clear_selection(self):
        logger.debug("Clearing all selected segments")
        for item in self.scene.items():
            if isinstance(item, SubtitleSegmentBar):
                item.deselect()
        self.selected_segments.clear()

    def show_context_menu(self, position):
        if self.selected_segments:
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
        logger.info("Deleting %d selected segments", len(self.selected_segments))
        self.subtitles_manager.delete_segments(self.selected_segments)

    def merge_segments(self):
        logger.info("Merging %d selected segments", len(self.selected_segments))
        self.subtitles_manager.merge_segments(self.selected_segments)

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)

    def notify_preview_time_change(self, timestamp: float):
        logger.debug("Preview time changed: %.2f seconds", timestamp)
        for listener in self.preview_time_listeners:
            listener(timestamp)

    def add_preview_time_listener(self, listener):
        if listener not in self.preview_time_listeners:
            logger.debug("Adding preview time listener: %s", listener)
            self.preview_time_listeners.append(listener)
        else:
            logger.warning("Listener already registered: %s", listener)

    def on_subtitles_changed(self, subtitles):
        logger.info(
            "Subtitles changed (%d segments)",
            len(subtitles.segments) if subtitles else 0,
        )
        self.clear_selection()
        video_duration = self.video_manager._video_duration
        self.update_timeline(subtitles, video_duration)

    def on_video_changed(self, video_path):
        logger.info("Video changed: %s", video_path)
        self.clear_selection()
        video_duration = self.video_manager._video_duration
        subtitles = self.subtitles_manager._subtitles
        self.update_timeline(subtitles, video_duration)
