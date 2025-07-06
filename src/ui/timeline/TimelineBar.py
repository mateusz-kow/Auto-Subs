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
    def __init__(self, subtitles_manager, video_manager, media_player):
        super().__init__()
        self.media_player = media_player

        # Main layout for the timeline bar
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setFixedHeight(VIDEO_BAR_Y + SUBTITLE_BAR_HEIGHT + BAR_HEIGHT)

        # Add the control buttons
        self._add_control_buttons(main_layout)

        # Add the segments bar
        self.segments_bar = SegmentsBar(subtitles_manager, video_manager)
        main_layout.addWidget(self.segments_bar)

    def _add_control_buttons(self, main_layout):
        """Add Pause/Play and Reset buttons to the right side."""
        # Create a container widget for the buttons
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Pause/Play button
        self.play_pause_button = QPushButton("⏯")  # Unicode for play/pause symbol
        self.play_pause_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.play_pause_button.clicked.connect(self._toggle_play_pause)
        self.play_pause_button.setFixedWidth(VIDEO_BAR_Y + SUBTITLE_BAR_HEIGHT + BAR_HEIGHT)
        button_layout.addWidget(self.play_pause_button)

        # Reset button
        self.reset_button = QPushButton("⏮")  # Unicode for reset symbol
        self.reset_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.reset_button.clicked.connect(self._reset_to_start)
        self.reset_button.setFixedWidth(VIDEO_BAR_Y + SUBTITLE_BAR_HEIGHT + BAR_HEIGHT)
        button_layout.addWidget(self.reset_button)

        # Add the button container to the main layout
        main_layout.addWidget(button_container)

    def _toggle_play_pause(self):
        """Toggle between play and pause states."""
        self.media_player.toggle_pause_state()

    def _reset_to_start(self):
        """Reset the video to the start (timestamp = 0)."""
        self.media_player.set_timestamp(0)
