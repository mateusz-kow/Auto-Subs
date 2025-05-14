from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from src.managers.StyleManager import StyleManager
from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.TranscriptionManager import TranscriptionManager
from src.managers.VideoManager import VideoManager
from ui.VideoLayout import VideoLayout
from ui.SubtitlesLayout import SubtitlesLayout
from ui.style_layout.StyleLayout import StyleLayout
from ui.TopBar import TopBar


class SubtitleEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subtitle Editor")

        self.style_manager = StyleManager()
        self.subtitles_manager = SubtitlesManager()
        self.video_manager = VideoManager()
        self.transcription_manager = TranscriptionManager()

        self.video_manager.add_video_listener(self.transcription_manager.on_video_changed)
        self.transcription_manager.add_transcription_listener(self.subtitles_manager.on_transcription_changed)

        self.video_layout = VideoLayout(self.style_manager, self.subtitles_manager, self.video_manager)
        self.style_layout = StyleLayout(self.style_manager)
        self.subtitles_layout = SubtitlesLayout(self.subtitles_manager, self.video_manager)
        self.top_bar = TopBar(self.style_manager, self.subtitles_manager, self.video_manager)

        # Układ główny - pionowy
        main_layout = QVBoxLayout(self)

        # Dodaj top bar
        main_layout.addWidget(self.top_bar)

        # Środkowy układ z edytorami
        center_layout = QHBoxLayout()
        center_layout.addLayout(self.style_layout, 2)
        center_layout.addLayout(self.video_layout, 4)
        center_layout.addLayout(self.subtitles_layout, 2)

        main_layout.addLayout(center_layout)
