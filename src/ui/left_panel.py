import asyncio
from logging import getLogger

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.managers.style_manager import StyleManager
from src.managers.subtitles_manager import SubtitlesManager
from src.subtitles.models import Subtitles, SubtitleWord
from src.ui.style.style_layout import StyleLayout
from src.ui.style.style_preset_view import StylePresetView
from src.ui.subtitles.segment_word_editor import SegmentWordEditor

logger = getLogger(__name__)


class LeftPanel(QWidget):
    """A widget for the left panel of the application.

    This panel contains a QStackedWidget to switch between the Style editor,
    the context-aware Segment Word Editor, and the Style Preset browser.
    """

    def __init__(
        self, style_manager: StyleManager, subtitles_manager: SubtitlesManager, parent: QWidget | None = None
    ) -> None:
        """Initialize the LeftPanel."""
        super().__init__(parent)
        self.style_manager = style_manager
        self.subtitles_manager = subtitles_manager
        self.current_segment_index: int | None = None

        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize the user interface of the left panel."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # --- Button Group for Manual Switching ---
        switcher_layout = QHBoxLayout()
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.style_button = QPushButton("Style Editor")
        self.style_button.setCheckable(True)
        switcher_layout.addWidget(self.style_button)
        self.button_group.addButton(self.style_button, 0)

        self.word_editor_button = QPushButton("Word Editor")
        self.word_editor_button.setCheckable(True)
        switcher_layout.addWidget(self.word_editor_button)
        self.button_group.addButton(self.word_editor_button, 1)

        self.presets_button = QPushButton("Presets")
        self.presets_button.setCheckable(True)
        switcher_layout.addWidget(self.presets_button)
        self.button_group.addButton(self.presets_button, 2)

        main_layout.addLayout(switcher_layout)

        # --- Stacked Widget to Hold Different Layouts ---
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # --- View 0: Style Layout ---
        self.style_layout = StyleLayout(self.style_manager)
        self.stacked_widget.addWidget(self.style_layout)

        # --- View 1: Segment Word Editor ---
        self.word_editor = SegmentWordEditor()
        self.stacked_widget.addWidget(self.word_editor)

        # --- View 2: Style Preset View ---
        self.preset_view = StylePresetView(self.style_manager)
        self.stacked_widget.addWidget(self.preset_view)

        # --- Initial State ---
        self.style_button.setChecked(True)
        self.stacked_widget.setCurrentIndex(0)
        self.word_editor_button.setEnabled(False)  # Disabled until a segment is selected

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.button_group.idClicked.connect(self.stacked_widget.setCurrentIndex)
        self.stacked_widget.currentChanged.connect(self._on_view_changed)

        # Connect signals from the word editor to the subtitles manager
        self.word_editor.word_changed.connect(self._on_word_changed)
        self.word_editor.add_new_word_requested.connect(self._on_add_word)
        self.word_editor.word_deleted.connect(self._on_delete_word)

    @Slot(int)
    def _on_view_changed(self, index: int) -> None:
        """Handle logic when switching views, like refreshing the preset list."""
        if index == 2:  # Preset view is now visible
            asyncio.create_task(self.preset_view.refresh_presets())

    @Slot(int)
    def show_editor_for_segment(self, segment_index: int) -> None:
        """Public slot to switch the view to the word editor and populate it
        with data for the specified segment.
        """
        if self.subtitles_manager.subtitles is None:
            return

        self.current_segment_index = segment_index
        segment = self.subtitles_manager.subtitles.segments[segment_index]
        self.word_editor.populate(segment, segment_index)

        # Switch the view
        self.word_editor_button.setEnabled(True)
        self.word_editor_button.setChecked(True)
        self.stacked_widget.setCurrentIndex(1)
        logger.info(f"LeftPanel switched to editor for segment {segment_index}.")

    @Slot(int, SubtitleWord)
    def _on_word_changed(self, word_index: int, new_word: SubtitleWord) -> None:
        if self.current_segment_index is not None:
            self.subtitles_manager.set_word(self.current_segment_index, word_index, new_word)

    @Slot()
    def _on_add_word(self) -> None:
        if self.current_segment_index is not None:
            self.subtitles_manager.add_empty_word(self.current_segment_index)

    @Slot(int)
    def _on_delete_word(self, word_index: int) -> None:
        if self.current_segment_index is not None:
            self.subtitles_manager.delete_word(self.current_segment_index, word_index)

    def on_subtitles_changed(self, subtitles: Subtitles) -> None:
        """Called when subtitles data changes to refresh the current view if necessary."""
        if (
            self.current_segment_index is not None
            and subtitles
            and self.current_segment_index < len(subtitles.segments)
        ):
            segment = subtitles.segments[self.current_segment_index]
            self.word_editor.populate(segment, self.current_segment_index)
        else:
            # The selected segment was deleted or data is cleared
            self.word_editor.clear_and_disable()
            self.word_editor_button.setEnabled(False)
            # Switch back to style view if the editor is currently active
            if self.stacked_widget.currentIndex() == 1:
                self.style_button.setChecked(True)
                self.stacked_widget.setCurrentIndex(0)
            self.current_segment_index = None
