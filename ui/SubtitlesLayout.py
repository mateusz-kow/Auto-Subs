import asyncio

from PySide6.QtWidgets import QVBoxLayout, QListWidget, QTreeWidget, QLineEdit, QPushButton, QHBoxLayout, QLabel, \
    QApplication, QMenu

from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.VideoManager import VideoManager
from src.subtitles.models import Subtitles, SubtitleWord
from src.transcriber import transcribe
from PySide6.QtWidgets import QTreeWidgetItem
from src.subtitles.models import SubtitleSegment
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import Qt
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QMenu

executor = ThreadPoolExecutor()


class SubtitlesLayout(QVBoxLayout):
    def __init__(self, subtitles_manager: SubtitlesManager, video_manager: VideoManager):
        super().__init__()
        self.subtitles_manager = subtitles_manager
        video_manager.add_video_listener(self.on_video_changed)
        subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)

        self.segment_list = QListWidget()
        self.segment_list.itemSelectionChanged.connect(self.load_words_for_segment)

        self.word_tree = QTreeWidget()
        self.word_tree.setHeaderLabels(["Text", "Start", "End"])
        self.word_tree.itemSelectionChanged.connect(self.display_selected_word)

        self.word_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.segment_list.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)

        self.word_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.word_tree.customContextMenuRequested.connect(self.show_word_context_menu)

        self.segment_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.segment_list.customContextMenuRequested.connect(self.show_segment_context_menu)

        self.word_input = QLineEdit()
        self.start_input = QLineEdit()
        self.end_input = QLineEdit()

        def labeled(label, widget):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(widget)
            return row

        save_button = QPushButton("Zapisz słowo")
        save_button.clicked.connect(self.save_word_edit)

        self.addWidget(self.segment_list)
        add_segment_button = QPushButton("Dodaj new_segment")
        add_segment_button.clicked.connect(self.add_segment)
        self.addWidget(add_segment_button)

        self.addWidget(self.word_tree)
        add_word_button = QPushButton("Dodaj słowo")
        add_word_button.clicked.connect(self.add_word)
        self.addWidget(add_word_button)

        self.addLayout(labeled("Word:", self.word_input))
        self.addLayout(labeled("Start:", self.start_input))
        self.addLayout(labeled("End:", self.end_input))
        self.addWidget(save_button)

        self.subtitles_generating_thread = None
        self.selected_word_index = 0
        self.selected_segment_index = 0

    def show_word_context_menu(self, position):
        menu = QMenu()
        merge_action = menu.addAction("Scal słowa")
        delete_action = menu.addAction("Usuń słowa")

        action = menu.exec(self.word_tree.viewport().mapToGlobal(position))
        if action == merge_action:
            self.merge_selected_words()
        elif action == delete_action:
            self.delete_selected_words()

    def show_segment_context_menu(self, position):
        menu = QMenu()
        delete_action = menu.addAction("Usuń segmenty")
        # Możesz dodać tu też scalanie segmentów później

        action = menu.exec(self.segment_list.viewport().mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_segments()

    def delete_selected_segments(self):
        selected = self.segment_list.selectedIndexes()
        if not selected:
            return

        self.subtitles_manager.delete_segments(selected)

    def add_segment(self):
        if not self.subtitles_manager.subtitles:
            self.subtitles_manager.subtitles = Subtitles([])

        self.subtitles_manager.add_empty_segment()

    def add_word(self):
        if self.subtitles_manager.subtitles is None or self.selected_segment_index is None:
            return

        self.subtitles_manager.add_empty_word(self.selected_segment_index)

    def load_words_for_segment(self):
        sel = self.segment_list.currentRow()
        if sel < 0:
            return
        self.selected_segment_index = sel
        segment = self.subtitles_manager.subtitles.segments[sel]
        self.word_tree.clear()
        for i, word in enumerate(segment.words):
            item = QTreeWidgetItem([word.text, f"{word.start:.2f}", f"{word.end:.2f}"])
            item.setData(0, 32, i)  # Qt.UserRole
            self.word_tree.addTopLevelItem(item)

    def display_selected_word(self):
        selected = self.word_tree.selectedItems()
        if not selected:
            return
        item = selected[0]
        self.selected_word_index = item.data(0, 32)
        word = self.subtitles_manager.subtitles.segments[self.selected_segment_index].words[self.selected_word_index]
        self.word_input.setText(word.text)
        self.start_input.setText(f"{word.start:.2f}")
        self.end_input.setText(f"{word.end:.2f}")

    def save_word_edit(self):
        if self.selected_segment_index is None or self.selected_word_index is None:
            return
        try:
            text = self.word_input.text().strip()
            start = float(self.start_input.text())
            end = float(self.end_input.text())
        except ValueError:
            return

        word = SubtitleWord(text, start, end)
        self.subtitles_manager.set_word(self.selected_segment_index, self.selected_word_index, word)

    async def async_transcribe(self, video_path: str):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, transcribe, video_path)

    def on_video_changed(self, video_path: str):
        self.segment_list.clear()
        self.word_tree.clear()

        asyncio.create_task(self._handle_video_change(video_path))

    async def _handle_video_change(self, video_path: str):
        transcription = await self.async_transcribe(video_path)
        self.subtitles_manager.set_subtitles(Subtitles.from_transcription(transcription))

    def update_segment_list(self):
        self.segment_list.clear()

        for i, segment in enumerate(self.subtitles_manager.subtitles.segments):
            text = f"{i + 1}. [{segment.start:.2f}-{segment.end:.2f}] {str(segment)}"
            self.segment_list.addItem(text)

    def on_subtitles_changed(self, subtitles: Subtitles):
        self.update_segment_list()
        self.load_words_for_segment()
