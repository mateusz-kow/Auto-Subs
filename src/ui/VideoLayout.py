import logging
import os
from threading import Thread, Timer

from PySide6.QtWidgets import QVBoxLayout

from src.utils.ffmpeg_utils import get_video_with_subtitles
from src.managers.StyleManager import StyleManager
from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.VideoManager import VideoManager
from src.subtitles.generator import SubtitleGenerator
from src.subtitles.models import Subtitles
from src.ui.MediaPlayer import MediaPlayer

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class VideoLayout(QVBoxLayout):
    def __init__(self, style_manager: StyleManager, subtitles_manager: SubtitlesManager, video_manager: VideoManager, media_player: MediaPlayer):
        super().__init__()
        style_manager.add_style_listener(self.on_style_changed)
        subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)
        self.style_manager = style_manager
        self.video_manager = video_manager
        self.subtitles_manager = subtitles_manager

        # Media player widget
        self.media_player = media_player
        self.addWidget(self.media_player)

        self._debounce_timer = None
        self._debounce_delay = 0.05

    def on_preview_time_changed(self, time: float):
        if self.video_manager._video_path and time >= 0:
            self.media_player.set_timestamp(int(time * 1000))  # Set video to the specified timestamp

    def generate_preview_video(self, timestamp: float):
        if self._debounce_timer:
            self._debounce_timer.cancel()  # Cancel previous timer

        def delayed_worker():
            logger.info(f"Generating preview at {timestamp:.2f} seconds...")

            def worker():
                try:
                    ass_path = SubtitleGenerator.to_ass(self.subtitles_manager.subtitles, self.style_manager.style, timestamp=timestamp)
                    preview_video_path = get_video_with_subtitles(
                        self.video_manager._video_path, ass_path
                    )

                    if preview_video_path and os.path.exists(preview_video_path):
                        self.media_player.set_media(preview_video_path)  # Set the preview image in the media player
                        logger.info("Preview video loaded.")
                    else:
                        logger.error("Preview video file not found or generation failed.")

                except Exception as e:
                    logger.exception("Error generating preview video.")

            Thread(target=worker).start()

        self._debounce_timer = Timer(self._debounce_delay, delayed_worker)
        self._debounce_timer.start()

    def on_subtitles_changed(self, subtitles: Subtitles):
        logger.info("Subtitles updated. Refreshing preview...")
        self.generate_preview_video(0)

    def on_style_changed(self, style: dict):
        logger.info("Style updated. Refreshing preview...")
        if self.subtitles_manager._subtitles:
            self.generate_preview_video(0)