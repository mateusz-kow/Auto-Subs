from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from src.managers.StyleManager import StyleManager
from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.TranscriptionManager import TranscriptionManager
from src.managers.VideoManager import VideoManager
from src.ui.MediaPlayer import MediaPlayer
from src.ui.VideoLayout import VideoLayout
from src.ui.SubtitlesLayout import SubtitlesLayout
from src.ui.style.StyleLayout import StyleLayout
from src.ui.TopBar import TopBar
from src.ui.timeline.TimelineBar import TimelineBar


class SubtitleEditorApp(QWidget):
    """Main application window for the Subtitle Editor."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Subs")

        # Initialize managers
        self._initialize_managers()

        # Initialize UI components
        self._initialize_ui()

        # Set up layout
        self._setup_layout()

    def _initialize_managers(self):
        """Initialize the managers and set up their interactions."""
        self.style_manager = StyleManager()
        self.subtitles_manager = SubtitlesManager()
        self.video_manager = VideoManager()
        self.transcription_manager = TranscriptionManager()

        # Connect managers
        self.video_manager.add_video_listener(
            self.transcription_manager.on_video_changed
        )
        self.video_manager.add_video_listener(self.subtitles_manager.on_video_changed)
        self.transcription_manager.add_transcription_listener(
            self.subtitles_manager.on_transcription_changed
        )

    def _initialize_ui(self):
        """Initialize the UI components."""
        self.media_player = MediaPlayer()
        self.video_layout = VideoLayout(
            self.style_manager,
            self.subtitles_manager,
            self.video_manager,
            self.media_player,
        )
        self.style_layout = StyleLayout(self.style_manager)
        self.subtitles_layout = SubtitlesLayout(
            self.subtitles_manager, self.video_manager
        )
        self.top_bar = TopBar(
            self.style_manager, self.subtitles_manager, self.video_manager
        )
        self.timeline_bar = TimelineBar(
            self.subtitles_manager, self.video_manager, self.media_player
        )

        self.timeline_bar.segments_bar.add_preview_time_listener(
            self.video_layout.on_preview_time_changed
        )

    def _setup_layout(self):
        """Set up the main layout of the application."""
        # Main vertical layout
        main_layout = QVBoxLayout(self)

        # Add top bar
        main_layout.addWidget(self.top_bar)

        # Center layout with editors
        center_layout = QHBoxLayout()
        center_layout.addWidget(self.style_layout, 2)
        center_layout.addLayout(self.video_layout, 4)

        # Add center layout to the main layout
        main_layout.addLayout(center_layout)

        # Add TimelineBar
        main_layout.addWidget(self.timeline_bar)
