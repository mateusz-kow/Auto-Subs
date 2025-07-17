from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from src.managers.StyleManager import StyleManager
from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.TranscriptionManager import TranscriptionManager
from src.managers.VideoManager import VideoManager
from src.ui.LeftPanel import LeftPanel
from src.ui.MediaPlayer import MediaPlayer
from src.ui.timeline.TimelineBar import TimelineBar
from src.ui.TopBar import TopBar
from src.ui.VideoLayout import VideoLayout


class SubtitleEditorApp(QMainWindow):
    """Main application window for the Subtitle Editor."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Auto Subs")

        # Initialize managers
        self._initialize_managers()

        # Initialize UI components
        self._initialize_ui()

        # Set up layout
        self._setup_layout()

        self.statusBar().showMessage("Ready")

    def _initialize_managers(self) -> None:
        """Initialize the managers and set up their interactions."""
        self.style_manager = StyleManager()
        self.subtitles_manager = SubtitlesManager()
        self.video_manager = VideoManager()
        self.transcription_manager = TranscriptionManager()

        # Connect managers
        self.video_manager.add_video_listener(self.transcription_manager.on_video_changed)
        self.video_manager.add_video_listener(self.subtitles_manager.on_video_changed)
        self.video_manager.add_video_listener(self.on_video_loaded_status)
        self.transcription_manager.add_transcription_listener(self.subtitles_manager.on_transcription_changed)

    def _initialize_ui(self) -> None:
        """Initialize the UI components."""
        self.media_player = MediaPlayer()
        self.video_layout = VideoLayout(
            self.style_manager,
            self.subtitles_manager,
            self.video_manager,
            self.media_player,
        )
        self.left_panel = LeftPanel(
            self.style_manager,
            self.subtitles_manager,
        )
        self.top_bar = TopBar(
            self.style_manager,
            self.subtitles_manager,
            self.video_manager,
            self.transcription_manager,
            self.statusBar(),
        )
        self.timeline_bar = TimelineBar(self.subtitles_manager, self.video_manager, self.media_player)

        # Connect timeline clicks to the LeftPanel's slot
        self.timeline_bar.segments_bar.segment_clicked.connect(self.left_panel.show_editor_for_segment)
        self.timeline_bar.segments_bar.segment_clicked.connect(self._seek_player_to_segment)

        # Connect subtitle changes to the LeftPanel to keep it in sync
        self.subtitles_manager.add_subtitles_listener(self.left_panel.on_subtitles_changed)
        # Connect video changes to TopBar to enable/disable transcribe button
        self.video_manager.add_video_listener(self.top_bar.on_video_changed)

        self.timeline_bar.segments_bar.add_preview_time_listener(self.video_layout.on_preview_time_changed)

    def _setup_layout(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.top_bar)

        center_layout = QHBoxLayout()
        center_layout.addWidget(self.left_panel, 2)
        center_layout.addLayout(self.video_layout, 4)
        main_layout.addLayout(center_layout)
        main_layout.addWidget(self.timeline_bar)

    @Slot(int)
    def _seek_player_to_segment(self, segment_index: int) -> None:
        """Seeks the media player to the start of the selected segment."""
        if self.subtitles_manager.subtitles:
            segment = self.subtitles_manager.subtitles.segments[segment_index]
            self.media_player.set_timestamp(int(segment.start * 1000))

    @Slot(Path)
    def on_video_loaded_status(self, video_path: Path) -> None:
        """Updates the status bar when a new video is loaded."""
        if video_path and video_path.exists():
            self.statusBar().showMessage(f"'{video_path.name}' loaded successfully.", 5000)
