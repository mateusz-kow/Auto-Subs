import logging
import os
from threading import Thread, Timer

from PySide6.QtWidgets import QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt

from src.utils.ffmpeg_utils import get_preview_image
from src.managers.StyleManager import StyleManager
from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.VideoManager import VideoManager
from src.subtitles.generator import SubtitleGenerator
from src.subtitles.models import Subtitles
from PySide6.QtGui import QPixmap

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class VideoLayout(QVBoxLayout):
    def __init__(self, style_manager: StyleManager, subtitles_manager: SubtitlesManager, video_manager: VideoManager):
        super().__init__()
        style_manager.add_style_listener(self.on_style_changed)
        subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)
        self.style_manager = style_manager
        self.video_manager = video_manager
        self.subtitles_manager = subtitles_manager

        # Preview image label
        self.image_label = QLabel("Video Frame Preview")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMaximumSize(1920, 1080)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(True)
        self.image_label.setStyleSheet("background-color: black;")
        self.addWidget(self.image_label)

        self._debounce_timer = None
        self._debounce_delay = 0.05

    def on_preview_time_changed(self, time: float):
        if self.video_manager._video_path and time >= 0:
            self.generate_preview_image(time)

    def generate_preview_image(self, timestamp: float):
        if self._debounce_timer:
            self._debounce_timer.cancel()  # Cancel previous timer

        def delayed_worker():
            logger.info(f"Generating preview at {timestamp:.2f} seconds...")

            def worker():
                try:
                    ass_path = SubtitleGenerator.to_ass(self.subtitles_manager.subtitles, self.style_manager.style, timestamp=timestamp)
                    preview_image_path = get_preview_image(
                        self.video_manager._video_path, ass_path, timestamp=timestamp
                    )

                    if preview_image_path and os.path.exists(preview_image_path):
                        pixmap = QPixmap(preview_image_path)
                        self.image_label.setPixmap(pixmap)
                        logger.info("Preview image loaded.")
                    else:
                        self.image_label.setText("Failed to generate frame.")
                        logger.error("Preview image file not found or generation failed.")

                except Exception as e:
                    logger.exception("Error generating preview image.")

            Thread(target=worker).start()

        self._debounce_timer = Timer(self._debounce_delay, delayed_worker)
        self._debounce_timer.start()

    def on_subtitles_changed(self, subtitles: Subtitles):
        logger.info("Subtitles updated. Refreshing preview...")
        self.generate_preview_image(0)

    def on_style_changed(self, style: dict):
        logger.info("Style updated. Refreshing preview...")
        if self.subtitles_manager._subtitles:
            self.generate_preview_image(0)



