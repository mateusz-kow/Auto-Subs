import asyncio
from logging import getLogger

from PySide6.QtWidgets import QSizePolicy, QVBoxLayout

from src.managers.StyleManager import StyleManager
from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.VideoManager import VideoManager
from src.subtitles.generator import SubtitleGenerator
from src.subtitles.models import Subtitles
from src.ui.MediaPlayer import MediaPlayer

logger = getLogger(__name__)


class VideoLayout(QVBoxLayout):
    """
    Layout for managing video playback and subtitle rendering.

    This class integrates video rendering with subtitle generation and applies
    dynamic style updates via associated managers.
    """

    def __init__(
        self,
        style_manager: StyleManager,
        subtitles_manager: SubtitlesManager,
        video_manager: VideoManager,
        media_player: MediaPlayer,
    ):
        """
        Initialize the layout with associated managers and media player widget.

        Args:
            style_manager (StyleManager): Manager for subtitle style settings.
            subtitles_manager (SubtitlesManager): Manager for subtitle content.
            video_manager (VideoManager): Manager for video file handling.
            media_player (MediaPlayer): The media player widget.
        """
        super().__init__()

        self.style_manager = style_manager
        self.subtitles_manager = subtitles_manager
        self.video_manager = video_manager
        self.media_player_widget = media_player

        self.media_player_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addWidget(self.media_player_widget)

        self._debounce_timer = None
        self._debounce_delay = 0.05

        style_manager.add_style_listener(self.on_style_changed)
        subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)

    def on_preview_time_changed(self, time: float) -> None:
        """
        Update the video timestamp when preview time changes.

        Args:
            time (float): Timestamp in seconds to preview.
        """
        if self.video_manager.video_path and time >= 0:
            logger.debug(f"Seeking to preview time: {time:.2f}s")
            self.media_player_widget.set_timestamp(int(time * 1000))

    def set_subtitles_only(self, subtitles: Subtitles) -> None:
        """
        Update the subtitles in the media player without reloading the video.

        Args:
            subtitles (Subtitles): The updated subtitles object.
        """
        logger.info("Updating subtitles only...")

        async def task():
            ass_path = await asyncio.to_thread(SubtitleGenerator.to_ass, subtitles, self.style_manager.style, None)
            self.media_player_widget.set_subtitles_only(ass_path)

        asyncio.create_task(task())

    def set_media_with_subtitles(self, video_path: str, subtitles: Subtitles) -> None:
        """
        Set both the video file and subtitles in the media player.

        Args:
            video_path (str): Path to the video file.
            subtitles (Subtitles): The updated subtitles object.
        """
        logger.info(f"Updating media: {video_path}")

        async def task():
            ass_path = await asyncio.to_thread(SubtitleGenerator.to_ass, subtitles, self.style_manager.style, None)
            self.media_player_widget.set_media(video_path, ass_path)

        asyncio.create_task(task())

    def on_subtitles_changed(self, subtitles: Subtitles) -> None:
        """
        Callback invoked when subtitle content is updated.

        Args:
            subtitles (Subtitles): The new subtitles object.
        """
        logger.info("Subtitles updated. Refreshing media with new subtitles.")
        self.set_media_with_subtitles(self.video_manager.video_path, self.subtitles_manager.subtitles)

    def on_style_changed(self, style: dict) -> None:
        """
        Callback invoked when subtitle style settings are updated.

        Args:
            style (dict): The new style dictionary.
        """
        logger.info("Style updated. Refreshing subtitles rendering.")
        if self.subtitles_manager.subtitles:
            self.set_subtitles_only(self.subtitles_manager.subtitles)
