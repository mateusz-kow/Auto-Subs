from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.VideoManager import VideoManager
from src.subtitles.models import Subtitles, SubtitleWord


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

        self.save_button = QPushButton("Save word")
        self.save_button.clicked.connect(self.save_word_edit)

        self.addWidget(self.segment_list)
        self.add_segment_button = QPushButton("Add new segment")
        self.add_segment_button.clicked.connect(self.add_segment)
        self.addWidget(self.add_segment_button)

        self.addWidget(self.word_tree)
        self.add_word_button = QPushButton("Add word")
        self.add_word_button.clicked.connect(self.add_word)
        self.addWidget(self.add_word_button)

        self.addLayout(labeled("Word:", self.word_input))
        self.addLayout(labeled("Start:", self.start_input))
        self.addLayout(labeled("End:", self.end_input))
        self.addWidget(self.save_button)

        self.subtitles_generating_thread = None
        self.selected_word_index = 0
        self.selected_segment_index = 0

    def show_word_context_menu(self, position):
        menu = QMenu()
        merge_action = menu.addAction("Merge words")
        delete_action = menu.addAction("Delete words")

        action = menu.exec(self.word_tree.viewport().mapToGlobal(position))
        if action == merge_action:
            self.merge_selected_words()
        elif action == delete_action:
            self.delete_selected_words()

    def show_segment_context_menu(self, position):
        menu = QMenu()
        delete_action = menu.addAction("Delete segments")
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
        if not self.subtitles_manager._subtitles:
            self.subtitles_manager._subtitles = Subtitles([])

        self.subtitles_manager.add_empty_segment()

    def add_word(self):
        if self.subtitles_manager._subtitles is None or self.selected_segment_index is None:
            return

        self.subtitles_manager.add_empty_word(self.selected_segment_index)

    def load_words_for_segment(self):
        sel = self.segment_list.currentRow()
        if sel < 0:
            return
        self.selected_segment_index = sel
        segment = self.subtitles_manager._subtitles.segments[sel]
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
        word = self.subtitles_manager._subtitles.segments[self.selected_segment_index].words[self.selected_word_index]
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

    def on_video_changed(self, video_path: str):
        self.segment_list.clear()
        self.word_tree.clear()

        self.save_button.setDisabled(True)
        self.add_segment_button.setDisabled(True)
        self.add_word_button.setDisabled(True)

    def update_segment_list(self, subtitles: Subtitles):
        self.segment_list.clear()

        for i, segment in enumerate(subtitles.segments):
            text = f"{i + 1}. [{segment.start:.2f}-{segment.end:.2f}] {str(segment)}"
            self.segment_list.addItem(text)

    def on_subtitles_changed(self, subtitles: Subtitles):
        self.update_segment_list(subtitles)
        self.load_words_for_segment()

        self.save_button.setDisabled(False)
        self.add_segment_button.setDisabled(False)
        self.add_word_button.setDisabled(False)
