import asyncio
import json
import subprocess
from logging import getLogger
from pathlib import Path
from typing import Any

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from src.config import STYLES_DIR, TEMP_DIR
from src.managers.style_manager import StyleManager
from src.subtitles.generator import SubtitleGenerator
from src.subtitles.models import Subtitles, SubtitleSegment, SubtitleWord
from src.utils.ffmpeg_utils import get_preview_image

logger = getLogger(__name__)


class StylePresetView(QWidget):
    """A widget to display, preview, and apply saved style presets.

    It scans a directory for .json style files, generates visual thumbnails,
    and allows users to apply a style with a single click.
    """

    def __init__(self, style_manager: StyleManager, parent: QWidget | None = None) -> None:
        """Initialize the StylePresetView.

        Args:
            style_manager: The manager for handling style state.
            parent: The parent widget.
        """
        super().__init__(parent)
        self.style_manager = style_manager
        self.style_files: dict[QListWidgetItem, Path] = {}
        self._blank_video_path: Path | None = None
        self._is_generating = False

        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.preset_list = QListWidget()
        self.preset_list.setFlow(QListWidget.Flow.LeftToRight)
        self.preset_list.setWrapping(True)
        self.preset_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.preset_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.preset_list.setIconSize(QSize(200, 100))
        self.preset_list.setSpacing(10)
        self.preset_list.setUniformItemSizes(True)

        main_layout.addWidget(self.preset_list)

    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        self.preset_list.itemClicked.connect(self._on_preset_clicked)

    async def _prepare_blank_video(self) -> None:
        """Create a short, blank video file to use as a canvas for rendering subtitle previews.

        This avoids the need for an actual video file when generating thumbnails.
        """
        output_path = TEMP_DIR / "blank_preview_video.mp4"
        if output_path.exists():
            self._blank_video_path = output_path
            return

        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=640x120:r=1:d=1",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]
        try:
            logger.info("Generating blank video for style previews...")
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                logger.error(f"Failed to create blank video: {stderr.decode()}")
                self._blank_video_path = None
            else:
                self._blank_video_path = output_path
                logger.info("Blank video created successfully.")
        except Exception as e:
            logger.error(f"Exception while creating blank video: {e}")
            self._blank_video_path = None

    async def refresh_presets(self) -> None:
        """Scan the styles directory and populate the list with presets."""
        if self._is_generating:
            logger.warning("Preset generation already in progress. Skipping refresh.")
            return

        if not self._blank_video_path:
            await self._prepare_blank_video()
            if not self._blank_video_path:
                QMessageBox.warning(
                    self, "Preview Error", "Could not generate canvas for previews. Check FFmpeg installation."
                )
                return

        self._is_generating = True
        self.preset_list.clear()
        self.style_files.clear()

        if not STYLES_DIR.exists() or not any(STYLES_DIR.iterdir()):
            self.preset_list.addItem("No styles found in user directory.")
            self._is_generating = False
            return

        json_files = sorted(STYLES_DIR.glob("*.json"))
        tasks = [self._generate_preset_item(file) for file in json_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, QListWidgetItem):
                self.preset_list.addItem(result)
            elif isinstance(result, Exception):
                logger.error(f"Failed to generate preset item: {result}")

        self._is_generating = False

    async def _generate_preset_item(self, style_path: Path) -> QListWidgetItem:
        """Generate a single QListWidgetItem for a style file, including its thumbnail."""

        def _read_style() -> dict[str, Any]:
            with open(style_path, encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise TypeError("Expected JSON root to be a dictionary")
                return data

        try:
            style_data = await asyncio.to_thread(_read_style)
        except (json.JSONDecodeError, OSError) as e:
            raise OSError(f"Failed to read or parse style file {style_path.name}: {e}") from e

        style_name = style_path.stem
        item = QListWidgetItem(style_name)
        item.setToolTip(f"Apply '{style_name}' style")
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.style_files[item] = style_path

        preview_path = await self._create_preview_image(style_data)
        if preview_path and preview_path.exists():
            item.setIcon(QIcon(str(preview_path)))

        return item

    async def _create_preview_image(self, style_data: dict[str, Any]) -> Path | None:
        """Render a preview image for a given style."""
        if not self._blank_video_path:
            return None

        sample_subtitles = Subtitles([SubtitleSegment([SubtitleWord("Sample Text", 0.1, 0.9)])])
        preview_settings = style_data.copy()
        preview_settings.update({"play_res_x": 640, "play_res_y": 120, "alignment": 8, "margin_v": 10})

        try:
            ass_path = await asyncio.to_thread(SubtitleGenerator.to_ass, sample_subtitles, preview_settings, None)
            preview_image_path = await asyncio.to_thread(get_preview_image, self._blank_video_path, ass_path, None, 0.5)
            return preview_image_path
        except Exception as e:
            logger.error(f"Error creating preview image for style '{style_data.get('title')}': {e}")
            return None

    @asyncSlot()  # type: ignore[misc]
    async def _on_preset_clicked(self, item: QListWidgetItem) -> None:
        """Handle clicking on a style preset to apply it."""
        style_path = self.style_files.get(item)
        if style_path:
            logger.info(f"Applying style from {style_path.name}")
            try:
                await asyncio.to_thread(self.style_manager.load_from_file, style_path)
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Failed to load style from {style_path.name}:\n{str(e)}")
