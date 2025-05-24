import logging

import vlc
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class MediaPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create VLC instance and media player
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def set_media(self, video_path: str, subtitle_path: str = None):
        """Set the media file and optional subtitle file."""
        if subtitle_path:
            media = self.instance.media_new(video_path, f":sub-file={subtitle_path}")
        else:
            media = self.instance.media_new(video_path)

        logger.info("Preparing to update video preview (media)...")
        self.media_player.set_media(media)

        # Set the video output to this widget
        self.media_player.set_hwnd(self.winId())  # For Windows
        self.media_player.play()
        while not self.media_player.is_playing():
            pass

        self.media_player.pause()
        self.media_player.next_frame()
        logger.info("Updated video preview (media)...")

    def _play_media(self):
        """Internal method to start playback after media is set."""
        logger.debug("Starting media playback...")
        self.media_player.play()

    def play(self):
        """Play the media."""
        self.media_player.play()

    def pause(self):
        """Pause the media."""
        self.media_player.pause()

    def set_timestamp(self, timestamp: int):
        """Set the playback position to the given timestamp (in milliseconds)."""
        self.media_player.set_time(timestamp)
