import logging
import os
from threading import Thread, Timer

from PySide6.QtWidgets import QVBoxLayout, QLabel, QSlider, QSizePolicy
from PySide6.QtCore import Qt, Signal

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
    ass_path_changed_signal = Signal(str)  # Define the signal

    def __init__(self, style_manager: StyleManager, subtitles_manager: SubtitlesManager, video_manager: VideoManager):
        super().__init__()
        style_manager.add_style_listener(self.on_style_changed)
        subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)
        self.style_manager = style_manager
        self.video_manager = video_manager
        self.subtitles_manager = subtitles_manager
        self.ass_path_changed_signal.connect(self.on_ass_path_changed)

        # Preview image label
        self.image_label = QLabel("Video Frame Preview")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMaximumSize(1920, 1080)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(True)
        self.image_label.setStyleSheet("background-color: black;")
        self.image_label.setScaledContents(True)
        self.addWidget(self.image_label)

        # Slider to seek video
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setEnabled(False)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1)  # Placeholder, will be updated dynamically
        self.slider.valueChanged.connect(self.on_slider_moved)
        self.addWidget(self.slider)

        self.ass_path: str = ""

        self._debounce_timer = None
        self._debounce_delay = 0.05

    def initialize_slider(self, subtitles: Subtitles):
        if not self.video_manager.video_path:
            logger.error("No video path set. Cannot initialize slider.")
            return

        if not subtitles:
            logger.error("No subtitles provided. Cannot initialize slider.")
            return

        timestamps = subtitles.timestamps

        if not timestamps:
            logger.error("No valid timestamps found in subtitles.")
            return

        self.slider.setMaximum(len(timestamps) - 1)
        self.slider.setEnabled(True)

        logger.info(f"Slider initialized with {len(timestamps)} positions.")

    def on_slider_moved(self, pos: int):
        if self.video_manager.video_path and pos < len(self.subtitles_manager.subtitles.timestamps):
            timestamp = self.subtitles_manager.subtitles.timestamps[pos]
            logger.debug(f"Slider moved to {timestamp:.2f}s")
            self.generate_preview_image(timestamp)

    def generate_preview_image(self, timestamp: float):
        if self._debounce_timer:
            self._debounce_timer.cancel()  # Cancel previous timer

        def delayed_worker():
            logger.info(f"Generating preview at {timestamp:.2f} seconds...")

            def worker():
                try:
                    ass_path = SubtitleGenerator.to_ass(self.subtitles_manager.subtitles, self.style_manager.style)
                    preview_image_path = get_preview_image(
                        self.video_manager.video_path, ass_path, timestamp=timestamp
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
        self.ass_path = SubtitleGenerator.to_ass(subtitles, self.style_manager.style)
        self.ass_path_changed_signal.emit(self.ass_path)  # Emit the signal

    def on_style_changed(self, style: dict):
        logger.info("Style updated. Refreshing preview...")
        if self.subtitles_manager.subtitles:
            self.ass_path = SubtitleGenerator.to_ass(self.subtitles_manager.subtitles, style)
            self.ass_path_changed_signal.emit(self.ass_path)  # Emit the signal

    def on_ass_path_changed(self, ass_path: str):
        subtitles = self.subtitles_manager.subtitles
        self.initialize_slider(subtitles)

        if len(subtitles.timestamps) > self.slider.value():
            self.generate_preview_image(subtitles.timestamps[self.slider.value()])
        elif len(subtitles.timestamps) > 0:
            self.generate_preview_image(subtitles.timestamps[0])
        else:
            self.image_label = QLabel("Video Frame Preview")
