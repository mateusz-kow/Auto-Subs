import asyncio
import logging

from PySide6.QtWidgets import QVBoxLayout, QSizePolicy

from src.managers.StyleManager import StyleManager
from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.VideoManager import VideoManager
from src.subtitles.generator import SubtitleGenerator
from src.subtitles.models import Subtitles
from src.ui.MediaPlayer import MediaPlayer

from src.utils.logger_config import get_logger
logger = get_logger(__name__)


class VideoLayout(QVBoxLayout):
    def __init__(self, style_manager: StyleManager, subtitles_manager: SubtitlesManager, video_manager: VideoManager,
                 media_player: MediaPlayer):
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

    def generate_preview_video(self):
        logger.info("Generating preview video...")

        async def task():
            ass_path = await asyncio.to_thread(
                SubtitleGenerator.to_ass,
                self.subtitles_manager.subtitles,
                self.style_manager.style,
                None
            )
            self.media_player_widget.set_media(self.video_manager._video_path, ass_path)

        asyncio.create_task(task())

    def on_subtitles_changed(self, subtitles: Subtitles):
        logger.info("Subtitles updated. Refreshing preview...")
        self.generate_preview_video()

    def on_style_changed(self, style: dict):
        logger.info("Style updated. Refreshing preview...")
        if self.subtitles_manager._subtitles:
            self.generate_preview_video()
