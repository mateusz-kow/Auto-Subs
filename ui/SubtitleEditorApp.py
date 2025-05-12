from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from ui.VideoLayout import VideoLayout
from ui.SubtitlesLayout import SubtitlesLayout
from ui.style_layout.StyleLayout import StyleLayout
from ui.TopBar import TopBar  # Zakładam, że zapisałeś go jako osobny plik


class SubtitleEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subtitle Editor")

        self.video_layout = VideoLayout()
        self.style_layout = StyleLayout()
        self.subtitles_layout = SubtitlesLayout()

        # Top bar z akcjami
        self.top_bar = TopBar()

        # Połączenia
        self.video_layout.addVideoListener(self.subtitles_layout.on_video_changed)
        self.subtitles_layout.add_subtitles_listener(self.video_layout.on_subtitles_changed)

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
