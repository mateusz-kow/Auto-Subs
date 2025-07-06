import asyncio

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMenu,
    QMessageBox,
    QPushButton,
    QWidget,
)
from qasync import asyncSlot

from src.managers.StyleManager import StyleManager
from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.VideoManager import VideoManager
from src.subtitles.generator import SubtitleGenerator
from src.utils.constants import STYLES_DIR
from src.utils.ffmpeg_utils import get_video_with_subtitles


class TopBar(QWidget):
    """TopBar widget containing the File and Style menus for the Subtitle Editor."""

    def __init__(
        self,
        style_manager: StyleManager,
        subtitles_manager: SubtitlesManager,
        video_manager: VideoManager,
    ):
        super().__init__()

        self.style_manager = style_manager
        self.subtitles_manager = subtitles_manager
        self.video_manager = video_manager

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(8)

        # File Menu
        self.file_btn = QPushButton("File")
        self.file_menu = QMenu(self.file_btn)
        self.file_btn.setMenu(self.file_menu)
        self.layout.addWidget(self.file_btn)

        # Style Menu
        self.style_btn = QPushButton("Style")
        self.style_menu = QMenu(self.style_btn)
        self.style_btn.setMenu(self.style_menu)
        self.layout.addWidget(self.style_btn)

        # File Menu Actions
        self._setup_file_menu()

        # Style Menu Actions
        self._setup_style_menu()

        self.layout.addStretch()

    def _setup_file_menu(self):
        import_mp4 = QAction("Import MP4", self)
        import_mp4.triggered.connect(self.import_mp4)

        export_txt = QAction("Export as TXT", self)
        export_txt.triggered.connect(self.export_txt)

        export_srt = QAction("Export as SRT", self)
        export_srt.triggered.connect(self.export_srt)

        export_ass = QAction("Export as ASS", self)
        export_ass.triggered.connect(self.export_ass)

        export_mp4 = QAction("Export as MP4", self)
        export_mp4.triggered.connect(self.export_mp4)

        self.file_menu.addActions([import_mp4])
        self.file_menu.addSeparator()
        self.file_menu.addActions([export_txt, export_srt, export_ass, export_mp4])

    def _setup_style_menu(self):
        reset_style = QAction("Reset to Default", self)
        reset_style.triggered.connect(self.reset_style_to_default)

        save_style = QAction("Save Style", self)
        save_style.triggered.connect(self.save_style_to_file)

        load_style = QAction("Load Style", self)
        load_style.triggered.connect(self.load_style_from_file)

        self.style_menu.addAction(reset_style)
        self.style_menu.addSeparator()
        self.style_menu.addActions([save_style, load_style])

    @asyncSlot()
    async def export_txt(self):
        """Export subtitles as a plain text (.txt) file."""
        path, _ = QFileDialog.getSaveFileName(self, "Export as TXT", "", "Text files (*.txt)")
        if path:
            try:
                await asyncio.to_thread(SubtitleGenerator.to_txt, self.subtitles_manager._subtitles, path)
                QMessageBox.information(self, "Export Successful", f"Subtitles exported as TXT:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export TXT:\n{str(e)}")

    @asyncSlot()
    async def export_srt(self):
        """Export subtitles in SubRip (.srt) format."""
        path, _ = QFileDialog.getSaveFileName(self, "Export as SRT", "", "SRT files (*.srt)")
        if path:
            try:
                await asyncio.to_thread(SubtitleGenerator.to_srt, self.subtitles_manager._subtitles, path)
                QMessageBox.information(self, "Export Successful", f"Subtitles exported as SRT:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export SRT:\n{str(e)}")

    @asyncSlot()
    async def export_ass(self):
        """Export subtitles in Advanced SubStation Alpha (.ass) format."""
        path, _ = QFileDialog.getSaveFileName(self, "Export as ASS", "", "ASS files (*.ass)")
        if path:
            try:
                await asyncio.to_thread(
                    SubtitleGenerator.to_ass,
                    self.subtitles_manager._subtitles,
                    self.style_manager.style,
                    path,
                )
                QMessageBox.information(self, "Export Successful", f"Subtitles exported as ASS:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export ASS:\n{str(e)}")

    @asyncSlot()
    async def export_mp4(self):
        """Export the video with embedded subtitles in MP4 format."""
        path, _ = QFileDialog.getSaveFileName(self, "Export as MP4", "", "MP4 files (*.mp4)")
        if path:
            try:
                ass_subtitles = await asyncio.to_thread(
                    SubtitleGenerator.to_ass,
                    self.subtitles_manager._subtitles,
                    self.style_manager.style,
                    None,
                )
                await asyncio.to_thread(
                    get_video_with_subtitles,
                    self.video_manager._video_path,
                    ass_subtitles,
                    path,
                )
                QMessageBox.information(self, "Export Successful", f"Video exported with subtitles:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export MP4:\n{str(e)}")

    @asyncSlot()
    async def import_mp4(self):
        """Prompt the user to select an MP4 file to import."""
        path, _ = QFileDialog.getOpenFileName(self, "Import MP4", "", "MP4 files (*.mp4)")
        if path:
            self.video_manager.set_video_path(path)

    # --- Style Menu Handlers ---

    def reset_style_to_default(self):
        """Reset subtitle styling to the default settings."""
        self.style_manager.reset_to_default()
        QMessageBox.information(self, "Style Reset", "Style has been reset to the default configuration.")

    @asyncSlot()
    async def save_style_to_file(self):
        """Save the current style to a JSON file."""
        path, _ = QFileDialog.getSaveFileName(self, "Save Style", str(STYLES_DIR), "JSON files (*.json)")
        if path:
            try:
                await asyncio.to_thread(self.style_manager.save_to_file, path)
                QMessageBox.information(self, "Style Saved", f"Style saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save style:\n{str(e)}")

    @asyncSlot()
    async def load_style_from_file(self):
        """Load subtitle styling from a JSON file."""
        path, _ = QFileDialog.getOpenFileName(self, "Load Style", str(STYLES_DIR), "JSON files (*.json)")
        if path:
            try:
                await asyncio.to_thread(self.style_manager.load_from_file, path)
                QMessageBox.information(self, "Style Loaded", f"Style loaded from:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Failed to load style:\n{str(e)}")
