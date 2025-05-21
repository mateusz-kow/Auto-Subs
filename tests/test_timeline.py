from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QObject

from src.ui.timeline.TimelineBar import TimelineBar


# Mock classes for SubtitlesManager and VideoManager
class MockSubtitlesManager(QObject):
    def __init__(self):
        super().__init__()
        self._subtitles = Subtitles([
            SubtitleSegment(0, 5, "Hello World"),
            SubtitleSegment(6, 10, "This is a test"),
            SubtitleSegment(12, 15, "Another subtitle")
        ])

    def add_subtitles_listener(self, listener):
        pass  # Mock method


class MockVideoManager(QObject):
    def __init__(self):
        super().__init__()
        self._video_duration = 40.0  # Example video duration

    def add_video_listener(self, listener):
        pass  # Mock method


# Example subtitle segment and subtitles classes
class SubtitleSegment:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return self.text


class Subtitles:
    def __init__(self, segments):
        self.segments = segments


# Main window to display the TimelineBar
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        subtitles_manager = MockSubtitlesManager()
        video_manager = MockVideoManager()
        self.timeline_bar = TimelineBar(subtitles_manager, video_manager)
        self.setCentralWidget(self.timeline_bar)

        # Initialize the timeline with mock data
        self.timeline_bar.update_timeline(subtitles_manager._subtitles, video_manager._video_duration)


# Test script to display the TimelineBar
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()