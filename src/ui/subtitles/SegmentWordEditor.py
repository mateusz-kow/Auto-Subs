from logging import getLogger

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.subtitles.models import SubtitleSegment, SubtitleWord

logger = getLogger(__name__)


class SegmentWordEditor(QWidget):
    """
    Provides a spreadsheet-like interface (QTableWidget) to edit words
    of a single subtitle segment.
    """

    # Signal -> emits (word_index, new_word_object)
    word_changed = Signal(int, SubtitleWord)
    # Signal -> emits word_index to be deleted
    word_deleted = Signal(int)
    # Signal -> requests a new empty word to be added
    add_new_word_requested = Signal()

    def __init__(self, parent=None):
        """Initialize the SegmentWordEditor."""
        super().__init__(parent)
        self._current_segment_index: int | None = None
        self._block_signals = False  # To prevent signals during population

        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Create and arrange the UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["#", "Text", "Start (s)", "End (s)"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.add_word_button = QPushButton("Add Word")
        self.delete_word_button = QPushButton("Delete Selected Word")

        layout.addWidget(self.table)
        layout.addWidget(self.add_word_button)
        layout.addWidget(self.delete_word_button)

    def _connect_signals(self) -> None:
        """Connect widget signals to their handlers."""
        self.table.itemChanged.connect(self._on_item_changed)
        self.add_word_button.clicked.connect(self.add_new_word_requested.emit)
        self.delete_word_button.clicked.connect(self._on_delete_word)

    def populate(self, segment: SubtitleSegment, segment_index: int) -> None:
        """
        Populate the table with words from the given segment.

        Args:
            segment: The subtitle segment to display.
            segment_index: The index of the segment in the main subtitles list.
        """
        self._block_signals = True  # Prevent itemChanged from firing
        self.table.clearContents()
        self._current_segment_index = segment_index

        self.table.setRowCount(len(segment.words))

        for row_idx, word in enumerate(segment.words):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(word.text))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{word.start:.3f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{word.end:.3f}"))
            # Make the ID column read-only
            self.table.item(row_idx, 0).setFlags(self.table.item(row_idx, 0).flags() & ~Qt.ItemFlag.ItemIsEditable)

        self._block_signals = False
        logger.info(f"Populated word editor for segment {segment_index} with {len(segment.words)} words.")
        self.setEnabled(True)

    def clear_and_disable(self) -> None:
        """Clears the table and disables the widget."""
        self.table.clearContents()
        self.table.setRowCount(0)
        self.setEnabled(False)
        self._current_segment_index = None
        logger.debug("Word editor cleared and disabled.")

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle changes made to a cell in the table."""
        if self._block_signals or self._current_segment_index is None:
            return

        row = item.row()
        try:
            text = self.table.item(row, 1).text().strip()
            start = float(self.table.item(row, 2).text())
            end = float(self.table.item(row, 3).text())

            if start < 0 or end < start:
                raise ValueError("Invalid timestamp values.")

            updated_word = SubtitleWord(text, start, end)
            self.word_changed.emit(row, updated_word)
            logger.debug(f"Word at index {row} changed to: {text}")

        except (ValueError, AttributeError) as e:
            logger.warning(f"Invalid data entered in word editor row {row}: {e}")
            # Consider adding user feedback here (e.g., cell turns red)

    def _on_delete_word(self) -> None:
        """Handle the delete word button click."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        word_index_to_delete = selected_rows[0].row()
        self.word_deleted.emit(word_index_to_delete)
        logger.info(f"Delete requested for word at index: {word_index_to_delete}")
