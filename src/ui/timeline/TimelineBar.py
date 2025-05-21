from PySide6.QtGui import QAction, QPen, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsTextItem, QMenu
from PySide6.QtCore import QPointF

from src.ui.timeline.Models import VideoGraphic, SegmentGraphic
from src.ui.timeline.constants import *


class TimelineBar(QGraphicsView):
    def __init__(self, subtitles_manager, video_manager):
        super().__init__()
        self.subtitles_manager = subtitles_manager
        self.video_manager = video_manager
        self.selected_segments = set()

        # Connect listeners
        video_manager.add_video_listener(self.on_video_changed)
        subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)

        # Graphics scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFixedHeight(SUBTITLE_BAR_Y + SUBTITLE_BAR_HEIGHT + BAR_HEIGHT)

    def update_timeline(self, subtitles, video_duration):
        """Update the timeline with video, subtitle segments, and markers."""
        self.scene.clear()

        if video_duration > 0:
            self._add_time_markers(video_duration)
            self._add_video_bar(video_duration)

        if subtitles and subtitles.segments:
            self._add_subtitle_segments(subtitles)

        total_duration = max(video_duration, subtitles.segments[-1].end if subtitles and subtitles.segments else 0)
        scene_width = max(SCENE_MIN_WIDTH, int(total_duration * TIME_SCALE_FACTOR))
        self.scene.setSceneRect(0, 0, scene_width, self.height())

    def _add_video_bar(self, video_duration):
        """Add the video bar to the timeline."""
        video_bar = VideoGraphic(video_duration)
        self.scene.addItem(video_bar)

    def _add_time_markers(self, video_duration):
        """Add time markers to the timeline."""
        for sec in range(0, int(video_duration) + 1, MINOR_MARKER_INTERVAL):
            x_pos = sec * TIME_SCALE_FACTOR
            is_major = (sec % MAJOR_MARKER_INTERVAL == 0)
            line_height = MAJOR_MARKER_HEIGHT if is_major else MINOR_MARKER_HEIGHT
            pen = QPen(Qt.GlobalColor.white, 1)  # White color for better visibility
            self.scene.addLine(x_pos, MARKER_Y, x_pos, MARKER_Y + line_height, pen)

            if is_major:
                marker_text = QGraphicsTextItem(f"{sec}s")
                marker_text.setDefaultTextColor(Qt.GlobalColor.white)  # White text
                marker_text.setPos(QPointF(x_pos - MARKER_TEXT_OFFSET / 2, MARKER_Y + line_height + 2))
                self.scene.addItem(marker_text)

    def _add_subtitle_segments(self, subtitles):
        """Add subtitle segments to the timeline."""
        for i, segment in enumerate(subtitles.segments):
            segment_item = SegmentGraphic(segment, i)
            self.scene.addItem(segment_item)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse clicks for selection and context menu."""
        scene_pos = self.mapToScene(event.pos())
        clicked_item = self.scene.itemAt(scene_pos, self.transform())

        if event.button() == Qt.MouseButton.LeftButton:
            if isinstance(clicked_item, SegmentGraphic):
                modifiers = event.modifiers()
                if modifiers == Qt.KeyboardModifier.ControlModifier:
                    # Toggle selection with Ctrl
                    self._toggle_segment_selection(clicked_item)
                elif modifiers == Qt.KeyboardModifier.ShiftModifier:
                    # Select range with Shift
                    self._select_range(clicked_item)
                else:
                    # Single selection
                    self.clear_selection()
                    self._select_segment(clicked_item)
            elif isinstance(clicked_item, VideoGraphic):
                # Update video progress on click
                clicked_item.mousePressEvent(event)
            else:
                self.clear_selection()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event)

    def _select_segment(self, clicked_item):
        """Select a subtitle segment."""
        self.selected_segments.add(clicked_item.index)
        clicked_item.select()

    def _toggle_segment_selection(self, clicked_item):
        """Toggle the selection of a segment."""
        if clicked_item.index in self.selected_segments:
            self.selected_segments.remove(clicked_item.index)
            clicked_item.deselect()
        else:
            self.selected_segments.add(clicked_item.index)
            clicked_item.select()

    def _select_range(self, clicked_item):
        """Select a range of segments."""
        if not self.selected_segments:
            self._select_segment(clicked_item)
            return

        # Determine the range
        last_selected = max(self.selected_segments)
        start = min(last_selected, clicked_item.index)
        end = max(last_selected, clicked_item.index)

        # Select all segments in the range
        for item in self.scene.items():
            if isinstance(item, SegmentGraphic) and start <= item.index <= end:
                self.selected_segments.add(item.index)
                item.select()

    def clear_selection(self):
        """Clear all selected segments."""
        for item in self.scene.items():
            if isinstance(item, SegmentGraphic):
                item.deselect()
        self.selected_segments.clear()

    def show_context_menu(self, event: QMouseEvent):
        """Show context menu for selected segments."""
        if self.selected_segments:
            menu = QMenu(self)
            delete_action = QAction("Delete Segments", self)
            merge_action = QAction("Merge Segments", self)

            delete_action.triggered.connect(self.delete_segments)
            merge_action.triggered.connect(self.merge_segments)

            menu.addAction(delete_action)
            menu.addAction(merge_action)
            menu.exec(event.globalPos())

    def delete_segments(self):
        """Delete selected segments."""
        self.subtitles_manager.delete_segments(self.selected_segments)

    def merge_segments(self):
        """Merge selected segments."""
        self.subtitles_manager.merge_segments(self.selected_segments)

    def wheelEvent(self, event: QWheelEvent):
        """Ensure scrolling is horizontal."""
        delta = event.angleDelta().y()
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)

    def on_subtitles_changed(self, subtitles):
        """Handle changes in subtitles."""
        self.clear_selection()
        video_duration = self.video_manager._video_duration
        self.update_timeline(subtitles, video_duration)

    def on_video_changed(self, video_path):
        """Handle changes in the video."""
        self.clear_selection()
        video_duration = self.video_manager._video_duration
        subtitles = self.subtitles_manager._subtitles
        self.update_timeline(subtitles, video_duration)
