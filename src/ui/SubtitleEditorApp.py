import asyncio
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolBar,
)
from qasync import asyncSlot

from src.managers.StyleManager import StyleManager
from src.managers.SubtitlesManager import SubtitlesManager
from src.managers.TranscriptionManager import TranscriptionManager
from src.managers.VideoManager import VideoManager
from src.subtitles.generator import SubtitleGenerator
from src.subtitles.models import Subtitles
from src.ui.LeftPanel import LeftPanel
from src.ui.MediaPlayer import MediaPlayer
from src.ui.timeline.TimelineBar import TimelineBar
from src.utils.ffmpeg_utils import get_video_with_subtitles


class SubtitleEditorApp(QMainWindow):
    """Main application window for the Subtitle Editor."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Auto Subs")

        self._initialize_managers()
        self._initialize_ui()
        self._setup_layout()
        self._setup_menus_and_toolbars()

        self.statusBar().showMessage("Ready")

    def _initialize_managers(self) -> None:
        """Initialize the managers and set up their interactions."""
        self.style_manager = StyleManager()
        self.subtitles_manager = SubtitlesManager()
        self.video_manager = VideoManager()
        self.transcription_manager = TranscriptionManager()

        # Connect managers
        self.video_manager.add_video_listener(self.transcription_manager.on_video_changed)
        self.video_manager.add_video_listener(self.subtitles_manager.on_video_changed)
        self.video_manager.add_video_listener(self.on_video_loaded_status)
        self.video_manager.add_video_listener(self._on_video_media_changed)
        self.transcription_manager.add_transcription_listener(self.subtitles_manager.on_transcription_changed)

    def _initialize_ui(self) -> None:
        """Initialize the UI components."""
        self.media_player = MediaPlayer()
        self.left_panel = LeftPanel(
            self.style_manager,
            self.subtitles_manager,
        )
        self.timeline_bar = TimelineBar(self.subtitles_manager, self.video_manager, self.media_player)

        # Connect UI component signals to slots
        self.timeline_bar.segments_bar.segment_clicked.connect(self.left_panel.show_editor_for_segment)
        self.timeline_bar.segments_bar.segment_clicked.connect(self._seek_player_to_segment)
        self.timeline_bar.segments_bar.add_preview_time_listener(self.on_preview_time_changed)

        # Connect manager signals to slots
        self.subtitles_manager.add_subtitles_listener(self.left_panel.on_subtitles_changed)
        self.subtitles_manager.add_subtitles_listener(self.on_subtitles_changed)
        self.style_manager.add_style_listener(self.on_style_changed)
        self.video_manager.add_video_listener(self._on_video_changed_for_transcribe_button)

    def _setup_layout(self) -> None:
        """Set up the main window layout with a central widget and dockable panels."""
        self.setCentralWidget(self.media_player)

        # Dock the editor panel
        self.left_dock_widget = QDockWidget("Editor Panel", self)
        self.left_dock_widget.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.left_dock_widget.setWidget(self.left_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.left_dock_widget)

        # Dock the timeline panel
        self.timeline_dock_widget = QDockWidget("Timeline", self)
        self.timeline_dock_widget.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea
        )
        self.timeline_dock_widget.setWidget(self.timeline_bar)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.timeline_dock_widget)

    def _setup_menus_and_toolbars(self) -> None:
        """Create and configure the menu bar and toolbars."""
        # --- File Menu ---
        file_menu = self.menuBar().addMenu("&File")
        import_action = QAction("Import Video", self)
        import_action.triggered.connect(self.import_mp4)
        file_menu.addAction(import_action)
        file_menu.addSeparator()
        export_txt_action = QAction("Export as TXT", self)
        export_txt_action.triggered.connect(self.export_txt)
        export_srt_action = QAction("Export as SRT", self)
        export_srt_action.triggered.connect(self.export_srt)
        export_ass_action = QAction("Export as ASS", self)
        export_ass_action.triggered.connect(self.export_ass)
        export_mp4_action = QAction("Export as MP4 (Hardsub)", self)
        export_mp4_action.triggered.connect(self.export_mp4)
        file_menu.addActions([export_txt_action, export_srt_action, export_ass_action, export_mp4_action])

        # --- Style Menu ---
        style_menu = self.menuBar().addMenu("&Style")
        reset_style_action = QAction("Reset to Default", self)
        reset_style_action.triggered.connect(self.reset_style_to_default)
        save_style_action = QAction("Save Style", self)
        save_style_action.triggered.connect(self.save_style_to_file)
        load_style_action = QAction("Load Style", self)
        load_style_action.triggered.connect(self.load_style_from_file)
        style_menu.addAction(reset_style_action)
        style_menu.addSeparator()
        style_menu.addActions([save_style_action, load_style_action])

        # --- View Menu ---
        view_menu = self.menuBar().addMenu("&View")
        toggle_editor_panel_action = self.left_dock_widget.toggleViewAction()
        toggle_editor_panel_action.setText("Toggle Editor Panel")
        view_menu.addAction(toggle_editor_panel_action)
        toggle_timeline_action = self.timeline_dock_widget.toggleViewAction()
        toggle_timeline_action.setText("Toggle Timeline Panel")
        view_menu.addAction(toggle_timeline_action)

        # --- Main Toolbar ---
        main_toolbar = QToolBar("Main Actions")
        self.addToolBar(main_toolbar)
        self.transcribe_btn = QPushButton("Transcribe Video")
        self.transcribe_btn.setEnabled(False)
        self.transcribe_btn.clicked.connect(self._on_transcribe_cancel_clicked)
        main_toolbar.addWidget(self.transcribe_btn)

        # Listen for transcription state changes to update button
        self.transcription_manager.add_transcription_listener(self._on_transcription_finished)
        self.transcription_manager.add_transcription_failed_listener(self._on_transcription_failed)
        self.transcription_manager.add_transcription_cancelled_listener(self._on_transcription_cancelled)

    # --- Video & Subtitle Rendering Slots ---

    def on_subtitles_changed(self, subtitles: Subtitles) -> None:
        """Callback to refresh subtitles when content changes."""
        if self.video_manager.video_path.exists():
            self._render_subtitles_on_player(subtitles)

    def on_style_changed(self, style: dict[str, Any]) -> None:
        """Callback to refresh subtitles when style changes."""
        if self.subtitles_manager.subtitles and self.video_manager.video_path.exists():
            self._render_subtitles_on_player(self.subtitles_manager.subtitles)

    def _render_subtitles_on_player(self, subtitles: Subtitles) -> None:
        """Generate and apply subtitles to the media player."""

        async def task() -> None:
            ass_path = await asyncio.to_thread(SubtitleGenerator.to_ass, subtitles, self.style_manager.style, None)
            self.media_player.set_subtitles_only(ass_path)

        asyncio.create_task(task())

    # --- UI Action Slots ---

    @Slot(int)
    def _seek_player_to_segment(self, segment_index: int) -> None:
        """Seeks the media player to the start of the selected segment."""
        if self.subtitles_manager.subtitles:
            segment = self.subtitles_manager.subtitles.segments[segment_index]
            self.media_player.set_timestamp(int(segment.start * 1000))

    @Slot(Path)
    def on_video_loaded_status(self, video_path: Path) -> None:
        """Updates the status bar when a new video is loaded."""
        if video_path and video_path.exists():
            self.statusBar().showMessage(f"'{video_path.name}' loaded successfully.", 5000)

    @Slot(Path)
    def _on_video_media_changed(self, video_path: Path) -> None:
        """Load a new video into the media player."""
        if video_path and video_path.exists():
            self.media_player.set_media(video_path, None)

    @Slot(float)
    def on_preview_time_changed(self, time: float) -> None:
        """Update the video timestamp when preview time changes."""
        if self.video_manager.video_path and time >= 0:
            self.media_player.set_timestamp(int(time * 1000))

    # --- Transcription Button Logic ---

    def _on_transcribe_cancel_clicked(self) -> None:
        """Handles clicks on the dynamic 'Transcribe/Cancel' button."""
        if self.transcribe_btn.text() == "Transcribe Video":
            self.statusBar().showMessage("Transcribing video... This may take a while.")
            self.transcription_manager.start_transcription()
            self.transcribe_btn.setText("Cancel Transcription")
        elif self.transcribe_btn.text() == "Cancel Transcription":
            self.transcription_manager.cancel_transcription()
            self.transcribe_btn.setText("Cancelling...")
            self.transcribe_btn.setEnabled(False)

    @Slot(Path)
    def _on_video_changed_for_transcribe_button(self, video_path: Path) -> None:
        """Enables or disables the transcribe button based on video presence."""
        self._reset_transcribe_button()

    def _on_transcription_finished(self, result: Any) -> None:
        """Resets the transcribe button after transcription is complete."""
        self.statusBar().showMessage("Transcription complete.", 5000)
        self._reset_transcribe_button()

    @Slot(Exception)
    def _on_transcription_failed(self, error: Exception) -> None:
        """Shows a failure message when transcription fails."""
        self.statusBar().showMessage(f"Transcription failed: {str(error)}", 5000)
        self._reset_transcribe_button()

    def _on_transcription_cancelled(self) -> None:
        """Resets the transcribe button after transcription is cancelled."""
        self.statusBar().showMessage("Transcription cancelled.", 5000)
        self._reset_transcribe_button()

    def _reset_transcribe_button(self) -> None:
        """Resets the transcribe button to its default state based on video presence."""
        self.transcribe_btn.setText("Transcribe Video")
        has_video = bool(self.video_manager.video_path and self.video_manager.video_path.exists())
        self.transcribe_btn.setEnabled(has_video)

    # --- Menu Action Slots (Import/Export/Style) ---

    @asyncSlot()  # type: ignore[misc]
    async def import_mp4(self) -> None:
        """Prompt the user to select a video file to import."""
        selected_path, _ = QFileDialog.getOpenFileName(self, "Import Video", "", "Video files (*.mp4 *.mkv *.avi)")
        if selected_path:
            path = Path(selected_path)
            self.video_manager.set_video_path(path)

    @asyncSlot()  # type: ignore[misc]
    async def export_txt(self) -> None:
        """Export subtitles as a plain text (.txt) file."""
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export as TXT", "", "TXT files (*.txt)")
        if not selected_path:
            return
        path = Path(selected_path)
        self.statusBar().showMessage(f"Exporting to {path.name}...")
        try:
            await asyncio.to_thread(SubtitleGenerator.to_txt, self.subtitles_manager.subtitles, path)
            self.statusBar().showMessage("Export complete.", 5000)
            QMessageBox.information(self, "Export Successful", f"Subtitles exported as TXT:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export TXT:\n{str(e)}")
        finally:
            self.statusBar().showMessage("Ready", 2000)

    @asyncSlot()  # type: ignore[misc]
    async def export_srt(self) -> None:
        """Export subtitles in SubRip (.srt) format."""
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export as SRT", "", "SRT files (*.srt)")
        if not selected_path:
            return
        path = Path(selected_path)
        self.statusBar().showMessage(f"Exporting to {path.name}...")
        try:
            await asyncio.to_thread(SubtitleGenerator.to_srt, self.subtitles_manager.subtitles, path)
            self.statusBar().showMessage("Export complete.", 5000)
            QMessageBox.information(self, "Export Successful", f"Subtitles exported as SRT:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export SRT:\n{str(e)}")
        finally:
            self.statusBar().showMessage("Ready", 2000)

    @asyncSlot()  # type: ignore[misc]
    async def export_ass(self) -> None:
        """Export subtitles in Advanced SubStation Alpha (.ass) format."""
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export as ASS", "", "ASS files (*.ass)")
        if not selected_path:
            return
        path = Path(selected_path)
        self.statusBar().showMessage(f"Exporting to {path.name}...")
        try:
            await asyncio.to_thread(
                SubtitleGenerator.to_ass,
                self.subtitles_manager.subtitles,
                self.style_manager.style,
                path,
            )
            self.statusBar().showMessage("Export complete.", 5000)
            QMessageBox.information(self, "Export Successful", f"Subtitles exported as ASS:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export ASS:\n{str(e)}")
        finally:
            self.statusBar().showMessage("Ready", 2000)

    @asyncSlot()  # type: ignore[misc]
    async def export_mp4(self) -> None:
        """Export the video with embedded subtitles in MP4 format."""
        selected_path, _ = QFileDialog.getSaveFileName(self, "Export as MP4", "", "MP4 files (*.mp4)")
        if not selected_path:
            return
        path = Path(selected_path)
        self.statusBar().showMessage(f"Exporting to {path.name}...")
        try:
            ass_subtitles = await asyncio.to_thread(
                SubtitleGenerator.to_ass,
                self.subtitles_manager.subtitles,
                self.style_manager.style,
                None,
            )
            await asyncio.to_thread(
                get_video_with_subtitles,
                self.video_manager.video_path,
                ass_subtitles,
                path,
            )
            self.statusBar().showMessage("Export complete.", 5000)
            QMessageBox.information(self, "Export Successful", f"Video exported with subtitles:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export MP4:\n{str(e)}")
        finally:
            self.statusBar().showMessage("Ready", 2000)

    def reset_style_to_default(self) -> None:
        """Reset subtitle styling to the default settings."""
        self.style_manager.reset_to_default()
        QMessageBox.information(self, "Style Reset", "Style has been reset to the default configuration.")

    @asyncSlot()  # type: ignore[misc]
    async def save_style_to_file(self) -> None:
        """Save the current style to a JSON file."""
        selected_path, _ = QFileDialog.getSaveFileName(self, "Save Style", "", "JSON files (*.json)")
        if selected_path:
            path = Path(selected_path)
            try:
                await asyncio.to_thread(self.style_manager.save_to_file, path)
                QMessageBox.information(self, "Style Saved", f"Style saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save style:\n{str(e)}")

    @asyncSlot()  # type: ignore[misc]
    async def load_style_from_file(self) -> None:
        """Load subtitle styling from a JSON file."""
        selected_path, _ = QFileDialog.getOpenFileName(self, "Load Style", "", "JSON files (*.json)")
        if selected_path:
            path = Path(selected_path)
            try:
                await asyncio.to_thread(self.style_manager.load_from_file, path)
                QMessageBox.information(self, "Style Loaded", f"Style loaded from:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Failed to load style:\n{str(e)}")
