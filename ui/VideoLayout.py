import logging
import os
from threading import Thread, Timer

from PySide6.QtWidgets import QVBoxLayout, QPushButton, QFileDialog, QLabel, QSlider, QSizePolicy
from PySide6.QtCore import Qt

from src.ffmpeg_manager import get_preview_image
from src.settings.StyleManager import StyleManager
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
    def __init__(self):
        super().__init__()

        # Load video button
        load_btn = QPushButton("📂 Load Video")
        load_btn.clicked.connect(self.change_video)
        self.addWidget(load_btn)

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

        self.video_path = None
        self.video_listeners: list = []
        self.subtitles = None
        self.ass_path: str = ""

        self.style = {
            "title": "Whisper Subtitles",
            "font": "Arial",
            "font_size": 55,
            "primary_color": "&H00FFFFFF",
            "alignment": 2,
            "margin_l": 10,
            "margin_r": 10,
            "margin_v": 500,
            "bold": -1,
            "italic": 0,
            "border_style": 1,
            "outline": 8,
            "shadow": 0,
            "encoding": 0
        }

        self._debounce_timer = None
        self._debounce_delay = 0.05

        StyleManager().add_style_listener(self.on_style_changed)

    def change_video(self):
        logger.info("Opening video selection dialog...")
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Select Video", "", "Video files (*.mp4 *.avi *.mkv)"
        )

        if not file_path:
            logger.warning("No video selected.")
            return

        if file_path == self.video_path:
            logger.info(f"Video '{file_path}' is already loaded.")
            return

        logger.info(f"Video selected: {file_path}")
        self.video_path = file_path

        for listener in self.video_listeners:
            listener(file_path)

    def addVideoListener(self, listener):
        self.video_listeners.append(listener)

    def initialize_slider(self, subtitles: Subtitles):
        if not self.video_path:
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
        if self.video_path and pos < len(self.subtitles.timestamps):
            timestamp = self.subtitles.timestamps[pos]
            logger.debug(f"Slider moved to {timestamp:.2f}s")
            self.generate_preview_image(timestamp)

    def generate_preview_image(self, timestamp: float):
        if self._debounce_timer:
            self._debounce_timer.cancel()  # Cancel previous timer

        def delayed_worker():
            logger.info(f"Generating preview at {timestamp:.2f} seconds...")

            def worker():
                try:
                    ass_path = SubtitleGenerator.to_ass(self.subtitles, self.style)
                    preview_image_path = get_preview_image(
                        self.video_path, ass_path, timestamp=timestamp
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
        self.subtitles = subtitles
        self.ass_path = SubtitleGenerator.to_ass(subtitles, self.style)
        self.initialize_slider(subtitles)

        if len(subtitles.timestamps) > self.slider.value():
            self.generate_preview_image(self.subtitles.timestamps[self.slider.value()])
        else:
            self.generate_preview_image(self.subtitles.timestamps[0])

    def on_style_changed(self, style: dict):
        logger.info("Style updated. Refreshing preview...")
        self.style = style
        if self.subtitles:
            self.ass_path = SubtitleGenerator.to_ass(self.subtitles, style)
            self.initialize_slider(self.subtitles)
            self.generate_preview_image(self.subtitles.timestamps[self.slider.value()])
