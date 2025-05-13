from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QMenu
)

from src.ffmpeg_manager import get_video_with_subtitles
from src.managers.StyleManager import StyleManager
from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.VideoManager import VideoManager
from src.subtitles.generator import SubtitleGenerator
from src.utils.constants import STYLES_DIR


class TopBar(QWidget):
    def __init__(self, style_manager: StyleManager, subtitles_manager: SubtitlesManager, video_manager: VideoManager):
        super().__init__()
        self.style_manager: StyleManager = style_manager
        self.subtitles_manager: SubtitlesManager = subtitles_manager
        self.video_manager: VideoManager = video_manager

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(8)

        # File button and menu
        self.file_btn = QPushButton("File")
        self.file_menu = QMenu(self.file_btn)
        self.file_btn.setMenu(self.file_menu)
        self.layout.addWidget(self.file_btn)

        # Style button and menu
        self.style_btn = QPushButton("Style")
        self.style_menu = QMenu(self.style_btn)
        self.style_btn.setMenu(self.style_menu)
        self.layout.addWidget(self.style_btn)

        # --- File Menu Actions ---

        # Import
        import_mp4 = QAction("Import MP4", self)
        import_mp4.triggered.connect(self.import_mp4)

        # Export
        export_srt = QAction("Export as SRT", self)
        export_srt.triggered.connect(self.export_srt)

        export_ass = QAction("Export as ASS", self)
        export_ass.triggered.connect(self.export_ass)

        export_mp4 = QAction("Export as MP4", self)
        export_mp4.triggered.connect(self.export_mp4)

        self.file_menu.addAction(import_mp4)
        self.file_menu.addSeparator()
        self.file_menu.addAction(export_srt)
        self.file_menu.addAction(export_ass)
        self.file_menu.addAction(export_mp4)

        # --- Style Menu Actions ---

        reset_style = QAction("Reset to Default", self)
        reset_style.triggered.connect(self.reset_style_to_default)

        change_default_style = QAction("Change Default Style", self)
        change_default_style.triggered.connect(self.change_default_style)

        save_style = QAction("Save Style", self)
        save_style.triggered.connect(self.save_style_to_file)

        load_style = QAction("Load Style", self)
        load_style.triggered.connect(self.load_style_from_file)

        self.style_menu.addAction(reset_style)
        self.style_menu.addAction(change_default_style)
        self.style_menu.addSeparator()
        self.style_menu.addAction(save_style)
        self.style_menu.addAction(load_style)

        self.layout.addStretch()

    # --- File Menu Handlers ---

    def import_mp4(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import MP4", "", "MP4 files (*.mp4)")
        if path:
            get_video_with_subtitles(path, SubtitleGenerator.to_ass(self.subtitles_manager.subtitles), output_path=path)
            QMessageBox.information(self, "Import", f"Imported MP4 from:\n{path}")
            # TODO: implement actual import logic

    def export_srt(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export as SRT", "", "SRT files (*.srt)")
        if path:

            QMessageBox.information(self, "Export", f"Exported SRT to:\n{path}")
            # TODO: implement actual export logic

    def export_ass(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export as ASS", "", "ASS files (*.ass)")
        if path:
            QMessageBox.information(self, "Export", f"Exported ASS to:\n{path}")
            # TODO: implement actual export logic

    def export_mp4(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export as MP4", "", "MP4 files (*.mp4)")
        if path:
            get_video_with_subtitles(path,
                                     SubtitleGenerator.to_ass(
                                         self.subtitles_manager.subtitles,
                                         self.style_manager.to_dict()),
                                     output_path=path)
            QMessageBox.information(self, "Export", f"Exported MP4 to:\n{path}")
            # TODO: implement actual export logic

    # --- Style Menu Handlers ---

    def reset_style_to_default(self):
        self.style_manager.reset_to_default()
        QMessageBox.information(self, "Style", "Style has been reset to default.")

    def change_default_style(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select New Default Style", str(STYLES_DIR), "JSON files (*.json)")
        if path:
            self.style_manager.set_as_default(path)
            QMessageBox.information(self, "Style", "Default style updated.")

    def save_style_to_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Style", str(STYLES_DIR), "JSON files (*.json)")
        if path:
            self.style_manager.save_to_file(path)
            QMessageBox.information(self, "Style", f"Style saved to:\n{path}")

    def load_style_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Style", str(STYLES_DIR), "JSON files (*.json)")
        if path:
            self.style_manager.load_from_file(path)
            QMessageBox.information(self, "Style", f"Style loaded from:\n{path}")
