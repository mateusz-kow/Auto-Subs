import os
from logging import getLogger
from pathlib import Path

from mpv import MPV
from PySide6.QtGui import QCloseEvent, QShowEvent
from PySide6.QtWidgets import QVBoxLayout, QWidget

logger = getLogger(__name__)


class MediaPlayer(QWidget):
    """A media player widget using the MPV library for video playback."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Initialize the MediaPlayer widget. MPV instance is initialized on first show.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.player: MPV | None = None
        self.mpv_initialized = False

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Set a minimum size for the widget
        self.setMinimumSize(320, 240)

    def _initialize_mpv(self) -> bool:
        """Initialize the MPV player instance. This should be called when the widget's window ID is valid."""
        if self.mpv_initialized:
            return True

        wid_val = self.winId()
        if int(wid_val) == 0:
            logger.error("Window ID is 0. MPV cannot be initialized yet.")
            return False

        try:
            logger.debug(f"Initializing MPV with wid: {wid_val}")
            self.player = MPV(wid=str(wid_val), loglevel="debug", keep_open="yes")
            self.mpv_initialized = True
            logger.info("MPV player initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MPV player: {e}", exc_info=True)
            self.player = None
            self.mpv_initialized = False
            return False

    def showEvent(self, event: QShowEvent) -> None:
        """Handle widget show event to initialize MPV when the widget becomes visible."""
        super().showEvent(event)
        if not self.mpv_initialized and self.isVisible() and not self._initialize_mpv():
            logger.error("MPV initialization failed during showEvent.")

    def _ensure_player_ready(self) -> bool:
        """Check if the MPV player is initialized and ready for commands."""
        if not self.player:
            logger.warning("MPV player is not initialized or has been terminated.")
            return False
        return True

    def set_subtitles_only(self, subtitle_path: Path) -> None:
        """
        Add a subtitle file for playback.

        Args:
            subtitle_path (str): Path to the subtitle file.
        """
        if not self._ensure_player_ready():
            return
        assert self.player is not None

        if not subtitle_path or not os.path.exists(subtitle_path):
            logger.warning(f"Invalid subtitle path: {subtitle_path}.")
            return

        logger.info(f"Setting subtitles: {subtitle_path}")
        try:
            if not self.player.filename:
                logger.warning("No media loaded. Subtitles will not be applied.")
                return

            self.pause()
            # TODO: Add throttling here in a try catch loop with maximum of 3 attempts
            self.player.sub_add(subtitle_path)
            self.player.sub_visibility = True
            self.player.command("sub_reload")
            logger.info("Subtitles set and reloaded.")
        except Exception as e:
            logger.error(f"Failed to set subtitles: {e}", exc_info=True)

    def set_media(self, video_path: Path, subtitle_path: Path | None = None) -> None:
        """
        Set the media file and optional subtitle file for playback.

        Args:
            video_path (str): Path to the video file.
            subtitle_path (str, optional): Path to the subtitle file.
        """
        if not self._ensure_player_ready():
            return
        assert self.player is not None

        if not video_path or not os.path.exists(video_path):
            logger.warning(f"Invalid video path: {video_path}.")
            return

        logger.info(f"Setting media: {video_path}, subtitles: {subtitle_path}")
        try:
            self.pause()
            self.player.loadfile(video_path, mode="replace")

            if subtitle_path:
                self.set_subtitles_only(subtitle_path)
        except Exception as e:
            logger.error(f"Failed to set media: {e}", exc_info=True)

    def play(self) -> None:
        """Play the media by unpausing."""
        if not self._ensure_player_ready():
            return
        assert self.player is not None

        try:
            if not self.player.filename:
                logger.warning("No media loaded. Cannot play.")
                return

            self.player.pause = False
            logger.info("Playback started.")
        except Exception as e:
            logger.error(f"Failed to play media: {e}", exc_info=True)

    def pause(self) -> None:
        """Pause media playback."""
        if not self._ensure_player_ready():
            return
        assert self.player is not None

        try:
            if not self.player.filename:
                logger.warning("No media loaded. Cannot pause.")
                return

            self.player.pause = True
            logger.info("Playback paused.")
        except Exception as e:
            logger.error(f"Failed to pause media: {e}", exc_info=True)

    def toggle_pause_state(self) -> None:
        """Toggle the pause state of the media. If paused, resume playback; otherwise, pause."""
        if not self._ensure_player_ready():
            return
        assert self.player is not None

        try:
            if not self.player.filename:
                logger.warning("No media loaded. Cannot toggle pause state.")
                return

            self.player.pause = not self.player.pause
            state = "paused" if self.player.pause else "playing"
            logger.info(f"Playback state toggled: {state}.")
        except Exception as e:
            logger.error(f"Failed to toggle pause state: {e}", exc_info=True)

    def set_timestamp(self, timestamp: int) -> None:
        """
        Set the playback position to the given timestamp.

        Args:
            timestamp (int): The timestamp in milliseconds.
        """
        if not self._ensure_player_ready():
            return
        assert self.player is not None

        try:
            if not self.player.filename:
                logger.warning("No media loaded. Cannot set timestamp.")
                return

            seconds = timestamp / 1000.0
            self.player.seek(seconds, reference="absolute", precision="exact")
            logger.info(f"Playback position set to {seconds:.3f}s.")
        except Exception as e:
            logger.error(f"Failed to set timestamp: {e}", exc_info=True)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle widget close event to release MPV resources.

        Args:
            event: The close event.
        """
        logger.info("Closing MediaPlayer.")
        if self.player:
            try:
                self.player.terminate()
                logger.info("MPV player terminated.")
            except Exception as e:
                logger.error(f"Error during MPV termination: {e}", exc_info=True)
            finally:
                self.player = None
                self.mpv_initialized = False
        super().closeEvent(event)
