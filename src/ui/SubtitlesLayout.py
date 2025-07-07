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
    """
    Layout widget for managing subtitle segments and words.

    Provides UI components for listing subtitle segments, viewing and editing
    individual words within segments, and managing context menus for operations
    like merging or deleting words and segments.
    """

    def __init__(self, subtitles_manager: SubtitlesManager, video_manager: VideoManager):
        """
        Initialize the subtitles layout with required managers.

        Args:
            subtitles_manager (SubtitlesManager): Manager handling subtitle data.
            video_manager (VideoManager): Manager handling video state.
        """
        super().__init__()

        self.subtitles_manager = subtitles_manager
        video_manager.add_video_listener(self.on_video_changed)
        subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)

        # Segment list widget
        self.segment_list = QListWidget()
        self.segment_list.itemSelectionChanged.connect(self.load_words_for_segment)
        self.segment_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.segment_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.segment_list.customContextMenuRequested.connect(self.show_segment_context_menu)

        # Word tree widget to display words with timings
        self.word_tree = QTreeWidget()
        self.word_tree.setHeaderLabels(["Text", "Start", "End"])
        self.word_tree.itemSelectionChanged.connect(self.display_selected_word)
        self.word_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.word_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.word_tree.customContextMenuRequested.connect(self.show_word_context_menu)

        # Input fields for editing word details
        self.word_input = QLineEdit()
        self.start_input = QLineEdit()
        self.end_input = QLineEdit()

        def labeled(label_text: str, widget) -> QHBoxLayout:
            """
            Helper to create a labeled input row.

            Args:
                label_text (str): Text label.
                widget: The input widget.

            Returns:
                QHBoxLayout: Layout containing label and widget.
            """
            row = QHBoxLayout()
            row.addWidget(QLabel(label_text))
            row.addWidget(widget)
            return row

        # Buttons
        self.save_button = QPushButton("Save word")
        self.save_button.clicked.connect(self.save_word_edit)

        self.add_segment_button = QPushButton("Add new segment")
        self.add_segment_button.clicked.connect(self.add_segment)

        self.add_word_button = QPushButton("Add word")
        self.add_word_button.clicked.connect(self.add_word)

        # Add widgets and layouts
        self.addWidget(self.segment_list)
        self.addWidget(self.add_segment_button)

        self.addWidget(self.word_tree)
        self.addWidget(self.add_word_button)

        self.addLayout(labeled("Word:", self.word_input))
        self.addLayout(labeled("Start:", self.start_input))
        self.addLayout(labeled("End:", self.end_input))
        self.addWidget(self.save_button)

        # Internal state
        self.selected_word_index = None
        self.selected_segment_index = None
        self.subtitles_generating_thread = None  # Placeholder if threaded generation is added later

    def show_word_context_menu(self, position):
        """
        Show context menu for word tree with options to merge or delete words.

        Args:
            position (QPoint): Position where the context menu was requested.
        """
        menu = QMenu()
        merge_action = menu.addAction("Merge words")
        delete_action = menu.addAction("Delete words")

        action = menu.exec(self.word_tree.viewport().mapToGlobal(position))
        if action == merge_action:
            self.merge_selected_words()
        elif action == delete_action:
            self.delete_selected_words()

    def show_segment_context_menu(self, position):
        """
        Show context menu for segment list with option to delete segments.

        Args:
            position (QPoint): Position where the context menu was requested.
        """
        menu = QMenu()
        delete_action = menu.addAction("Delete segments")
        # Future: Add segment merging action here

        action = menu.exec(self.segment_list.viewport().mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_segments()

    def delete_selected_segments(self):
        """Delete currently selected subtitle segments."""
        selected = self.segment_list.selectedIndexes()
        if not selected:
            return
        self.subtitles_manager.delete_segments([x.row() for x in selected])

    def add_segment(self):
        """Add a new empty subtitle segment."""
        if not self.subtitles_manager._subtitles:
            self.subtitles_manager._subtitles = Subtitles([])

        self.subtitles_manager.add_empty_segment()

    def add_word(self):
        """Add a new empty word to the currently selected segment."""
        if self.subtitles_manager._subtitles is None or self.selected_segment_index is None:
            return
        self.subtitles_manager.add_empty_word(self.selected_segment_index)

    def load_words_for_segment(self):
        """Load words from the selected segment into the word tree."""
        sel = self.segment_list.currentRow()
        if sel < 0:
            return
        self.selected_segment_index = sel
        segment = self.subtitles_manager._subtitles.segments[sel]
        self.word_tree.clear()
        for i, word in enumerate(segment.words):
            item = QTreeWidgetItem([word.text, f"{word.start:.2f}", f"{word.end:.2f}"])
            item.setData(0, 32, i)
            self.word_tree.addTopLevelItem(item)

    def display_selected_word(self):
        """Display the details of the currently selected word for editing."""
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
        """Save changes made to the selected word."""
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
        """
        Reset UI when video changes.

        Args:
            video_path (str): The new video path.
        """
        self.segment_list.clear()
        self.word_tree.clear()
        self.save_button.setDisabled(True)
        self.add_segment_button.setDisabled(True)
        self.add_word_button.setDisabled(True)

    def update_segment_list(self, subtitles: Subtitles):
        """
        Populate segment list widget from current subtitles.

        Args:
            subtitles (Subtitles): The current subtitles object.
        """
        self.segment_list.clear()
        for i, segment in enumerate(subtitles.segments):
            text = f"{i + 1}. [{segment.start:.2f}-{segment.end:.2f}] {str(segment)}"
            self.segment_list.addItem(text)

    def on_subtitles_changed(self, subtitles: Subtitles):
        """
        Callback for when subtitles update.

        Args:
            subtitles (Subtitles): The updated subtitles.
        """
        self.update_segment_list(subtitles)
        self.load_words_for_segment()
        self.save_button.setDisabled(False)
        self.add_segment_button.setDisabled(False)
        self.add_word_button.setDisabled(False)

    # Placeholder methods for completeness (implement as needed)
    def merge_selected_words(self):
        """Merge selected words into one."""
        pass  # To be implemented

    def delete_selected_words(self):
        """Delete selected words."""
        pass  # To be implemented
