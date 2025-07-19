from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.managers.subtitles_manager import SubtitlesManager
from src.managers.video_manager import VideoManager
from src.ui.media_player import MediaPlayer
from src.ui.timeline.constants import SUBTITLE_BAR_HEIGHT, SUBTITLE_BAR_Y
from src.ui.timeline.SegmentsBar import SegmentsBar


class TimelineBar(QWidget):
    """
    A widget representing the timeline bar of a video editor interface.

    This bar includes playback control buttons and a visual segments bar that
    displays subtitle segments and video markers. It is designed to be resizeable.

    Attributes:
        media_player: An object that controls video playback.
        segments_bar (SegmentsBar): The widget displaying subtitle segments.
    """

    def __init__(
        self, subtitles_manager: SubtitlesManager, video_manager: VideoManager, media_player: MediaPlayer
    ) -> None:
        """
        Initialize the TimelineBar widget.

        Args:
            subtitles_manager: Manager handling subtitle data.
            video_manager: Manager responsible for video information.
            media_player: Controller for video playback.
        """
        super().__init__()

        self.media_player = media_player

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(5)

        # Set a minimum height to ensure the timeline remains usable.
        self.setMinimumHeight(SUBTITLE_BAR_Y + SUBTITLE_BAR_HEIGHT + 10)

        # Create components
        button_container = self._create_control_buttons()
        self.segments_bar = SegmentsBar(subtitles_manager, video_manager)

        main_layout.addWidget(button_container, 0)
        main_layout.addWidget(self.segments_bar, 1)

    def _create_control_buttons(self) -> QWidget:
        """
        Create and return a widget containing the playback control buttons.

        Returns:
            QWidget: The container widget with the buttons.
        """
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(2)

        self.play_pause_button = QPushButton("⏯")  # Play/Pause symbol
        self.play_pause_button.setToolTip("Play/Pause (Space)")
        self.play_pause_button.clicked.connect(self._toggle_play_pause)

        self.reset_button = QPushButton("⏮")  # Rewind to start symbol
        self.reset_button.setToolTip("Go to Start")
        self.reset_button.clicked.connect(self._reset_to_start)

        button_layout.addWidget(self.play_pause_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()

        return button_container

    def _toggle_play_pause(self) -> None:
        """Toggle the playback state of the media player."""
        self.media_player.toggle_pause_state()

    def _reset_to_start(self) -> None:
        """Reset the media player's playback position to the beginning."""
        self.media_player.set_timestamp(0)
