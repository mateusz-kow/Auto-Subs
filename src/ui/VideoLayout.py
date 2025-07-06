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
    def __init__(
        self,
        style_manager: StyleManager,
        subtitles_manager: SubtitlesManager,
        video_manager: VideoManager,
        media_player: MediaPlayer,
    ):
        super().__init__()
        style_manager.add_style_listener(self.on_style_changed)
        subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)
        self.style_manager = style_manager
        self.video_manager = video_manager
        self.subtitles_manager = subtitles_manager

        # Media player widget
        self.media_player_widget = media_player
        self.media_player_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addWidget(self.media_player_widget)

        self._debounce_timer = None
        self._debounce_delay = 0.05

    def on_preview_time_changed(self, time: float):
        if self.video_manager._video_path and time >= 0:
            self.media_player_widget.set_timestamp(int(time * 1000))  # Set video to the specified timestamp

    def set_subtitles_only(self, subtitles: Subtitles):
        """
        Update only the subtitles in the media player.

        Args:
            subtitles (Subtitles): The updated subtitles object.
        """
        logger.info("Updating subtitles only...")

        async def task():
            ass_path = await asyncio.to_thread(SubtitleGenerator.to_ass, subtitles, self.style_manager.style, None)
            self.media_player_widget.set_subtitles_only(ass_path)

        asyncio.create_task(task())

    def set_media_with_subtitles(self, video_path: str, subtitles: Subtitles):
        """
        Update the video and subtitles in the media player.

        Args:
            video_path (str): Path to the video file.
            subtitles (Subtitles): The updated subtitles object.
        """
        logger.info("Updating video and subtitles...")

        async def task():
            ass_path = await asyncio.to_thread(SubtitleGenerator.to_ass, subtitles, self.style_manager.style, None)
            self.media_player_widget.set_media(video_path, ass_path)

        asyncio.create_task(task())

    def on_subtitles_changed(self, subtitles: Subtitles):
        logger.info("Subtitles updated. Refreshing subtitles...")
        self.set_media_with_subtitles(self.video_manager._video_path, self.subtitles_manager.subtitles)

    def on_style_changed(self, style: dict):
        logger.info("Style updated. Refreshing video and subtitles...")
        if self.subtitles_manager._subtitles:
            self.set_subtitles_only(self.subtitles_manager._subtitles)
