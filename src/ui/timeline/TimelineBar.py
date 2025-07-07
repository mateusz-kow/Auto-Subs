from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from src.ui.timeline.constants import BAR_HEIGHT, SUBTITLE_BAR_HEIGHT, VIDEO_BAR_Y
from src.ui.timeline.SegmentsBar import SegmentsBar


class TimelineBar(QWidget):
    """
    A widget representing the timeline bar of a video editor interface.

    This bar includes:
        - Playback control buttons (play/pause, reset).
        - A visual segments bar displaying subtitle segments and video markers.

    Attributes:
        media_player: An object that controls video playback.
        segments_bar (SegmentsBar): The widget displaying subtitle segments.
    """

    def __init__(self, subtitles_manager, video_manager, media_player):
        """
        Initialize the TimelineBar widget.

        Args:
            subtitles_manager: Manager handling subtitle data.
            video_manager: Manager responsible for video information.
            media_player: Controller for video playback.
        """
        super().__init__()

        self.media_player = media_player

        # Configure main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setFixedHeight(VIDEO_BAR_Y + SUBTITLE_BAR_HEIGHT + BAR_HEIGHT)

        # Add control buttons and segments bar
        self._add_control_buttons(main_layout)
        self.segments_bar = SegmentsBar(subtitles_manager, video_manager)
        main_layout.addWidget(self.segments_bar)

    def _add_control_buttons(self, main_layout):
        """
        Create and add the playback control buttons (play/pause, reset) to the layout.

        Args:
            main_layout (QHBoxLayout): The parent layout to which the controls are added.
        """
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        button_layout.setContentsMargins(0, 0, 0, 0)

        button_size = VIDEO_BAR_Y + SUBTITLE_BAR_HEIGHT + BAR_HEIGHT

        # Play/Pause button
        self.play_pause_button = QPushButton("⏯")  # Unicode for play/pause symbol
        self.play_pause_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.play_pause_button.setFixedWidth(button_size)
        self.play_pause_button.clicked.connect(self._toggle_play_pause)
        button_layout.addWidget(self.play_pause_button)

        # Reset button
        self.reset_button = QPushButton("⏮")  # Unicode for reset symbol
        self.reset_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.reset_button.setFixedWidth(button_size)
        self.reset_button.clicked.connect(self._reset_to_start)
        button_layout.addWidget(self.reset_button)

        main_layout.addWidget(button_container)

    def _toggle_play_pause(self):
        """Toggle the playback state of the media player."""
        self.media_player.toggle_pause_state()

    def _reset_to_start(self):
        """Reset the media player's playback position to the beginning."""
        self.media_player.set_timestamp(0)
