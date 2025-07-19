# src/ui/subtitle_editor_app.py
import asyncio
import json
import uuid
import zipfile
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolBar,
)
from qasync import asyncSlot

from src.config import STYLES_DIR, TEMP_DIR
from src.managers.style_manager import StyleManager
from src.managers.subtitles_manager import SubtitlesManager
from src.managers.transcription_manager import TranscriptionManager
from src.managers.video_manager import VideoManager
from src.subtitles.generator import SubtitleGenerator
from src.subtitles.models import Subtitles
from src.ui.left_panel import LeftPanel
from src.ui.media_player import MediaPlayer
from src.ui.timeline.timeline_bar import TimelineBar
from src.utils.ffmpeg_utils import get_video_with_subtitles


class SubtitleEditorApp(QMainWindow):
    """Main application window for the Subtitle Editor."""

    def __init__(self) -> None:
        """Initialize the SubtitleEditorApp."""
        super().__init__()
        self._current_project_path: Path | None = None
        self._update_window_title()

        self._initialize_managers()
        self._initialize_ui()
        self._setup_layout()
        self._setup_menus_and_toolbars()
        self._connect_observers()

        self.statusBar().showMessage("Ready")

    def _initialize_managers(self) -> None:
        """Initialize the managers and set up their interactions."""
        self.style_manager = StyleManager()
        self.subtitles_manager = SubtitlesManager()
        self.video_manager = VideoManager()
        self.transcription_manager = TranscriptionManager()

    def _connect_observers(self) -> None:
        """Connect the managers to their respective observers."""
        managers = (self.style_manager, self.subtitles_manager, self.video_manager, self.transcription_manager)

        # UI components and other managers that listen to manager events
        listeners = (
            self,  # The main window itself
            self.subtitles_manager,  # Listens to transcription and video events
            self.transcription_manager,  # Listens to video events
            self.left_panel,  # Listens to subtitle events
            self.left_panel.style_layout,  # Listens for style loaded events
            self.timeline_bar.segments_bar,  # Listens to subtitle and video events
        )

        for manager in managers:
            for listener in listeners:
                if manager is listener:  # A manager should not listen to itself via this mechanism
                    continue
                manager.register_listener(listener)

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

        open_project_action = QAction("Open Project...", self)
        open_project_action.setShortcut(QKeySequence.StandardKey.Open)
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)

        file_menu.addSeparator()

        save_project_action = QAction("Save Project", self)
        save_project_action.setShortcut(QKeySequence.StandardKey.Save)
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)

        save_project_as_action = QAction("Save Project As...", self)
        save_project_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_project_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_project_as_action)

        file_menu.addSeparator()

        import_action = QAction("Import Video...", self)
        import_action.triggered.connect(self.import_mp4)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        export_txt_action = QAction("Export as TXT...", self)
        export_txt_action.triggered.connect(self.export_txt)
        export_srt_action = QAction("Export as SRT...", self)
        export_srt_action.triggered.connect(self.export_srt)
        export_ass_action = QAction("Export as ASS...", self)
        export_ass_action.triggered.connect(self.export_ass)
        export_mp4_action = QAction("Export as MP4 (Hardsub)...", self)
        export_mp4_action.triggered.connect(self.export_mp4)
        file_menu.addActions([export_txt_action, export_srt_action, export_ass_action, export_mp4_action])

        # --- Style Menu ---
        style_menu = self.menuBar().addMenu("&Style")
        reset_style_action = QAction("Reset to Default", self)
        reset_style_action.triggered.connect(self.reset_style_to_default)
        save_style_action = QAction("Save Style As...", self)
        save_style_action.triggered.connect(self.save_style_to_file)
        load_style_action = QAction("Load Style...", self)
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

    # --- Listener Callbacks ---

    def on_video_changed(self, video_path: Path) -> None:
        """Handle video change events."""
        if video_path and video_path.exists():
            self.statusBar().showMessage(f"'{video_path.name}' loaded successfully.", 5000)
            self.media_player.set_media(video_path, None)
        self._reset_transcribe_button()

    def on_subtitles_changed(self, subtitles: Subtitles) -> None:
        """Callback to refresh subtitles when content changes."""
        if self.video_manager.video_path.exists():
            self._render_subtitles_on_player(subtitles)

    def on_style_changed(self, style: dict[str, Any]) -> None:
        """Callback to refresh subtitles when style changes."""
        if self.subtitles_manager.subtitles and self.video_manager.video_path.exists():
            self._render_subtitles_on_player(self.subtitles_manager.subtitles)

    def on_transcription_changed(self, result: Any) -> None:
        """Resets the transcribe button after transcription is complete."""
        self.statusBar().showMessage("Transcription complete.", 5000)
        self._reset_transcribe_button()

    def on_transcription_failed(self, error: Exception) -> None:
        """Shows a failure message when transcription fails."""
        self.statusBar().showMessage(f"Transcription failed: {str(error)}", 5000)
        self._reset_transcribe_button()
        QMessageBox.critical(self, "Transcription Error", f"Could not transcribe video:\n{str(error)}")

    def on_transcription_cancelled(self, data: dict[str, Any]) -> None:
        """Resets the transcribe button after transcription is cancelled."""
        self.statusBar().showMessage("Transcription cancelled.", 5000)
        self._reset_transcribe_button()

    # --- UI Action Slots and Helpers ---

    def _render_subtitles_on_player(self, subtitles: Subtitles) -> None:
        """Generate and apply subtitles to the media player."""

        async def task() -> None:
            ass_path = await asyncio.to_thread(SubtitleGenerator.to_ass, subtitles, self.style_manager.style, None)
            self.media_player.set_subtitles_only(ass_path)

        asyncio.create_task(task())

    @Slot(int)
    def _seek_player_to_segment(self, segment_index: int) -> None:
        """Seek the media player to the start of the selected segment."""
        if self.subtitles_manager.subtitles:
            segment = self.subtitles_manager.subtitles.segments[segment_index]
            self.media_player.set_timestamp(int(segment.start * 1000))

    @Slot(float)
    def on_preview_time_changed(self, time: float) -> None:
        """Update the video timestamp when preview time changes."""
        if self.video_manager.video_path and time >= 0:
            self.media_player.set_timestamp(int(time * 1000))

    # --- Transcription Button Logic ---

    def _on_transcribe_cancel_clicked(self) -> None:
        """Handle clicks on the dynamic 'Transcribe/Cancel' button."""
        if self.transcribe_btn.text() == "Transcribe Video":
            self.statusBar().showMessage("Transcribing video... This may take a while.")
            self.transcription_manager.start_transcription()
            self.transcribe_btn.setText("Cancel Transcription")
        elif self.transcribe_btn.text() == "Cancel Transcription":
            self.transcription_manager.cancel_transcription()
            self.transcribe_btn.setText("Cancelling...")
            self.transcribe_btn.setEnabled(False)

    def _reset_transcribe_button(self) -> None:
        """Reset the transcribe button to its default state based on video presence."""
        self.transcribe_btn.setText("Transcribe Video")
        has_video = bool(self.video_manager.video_path and self.video_manager.video_path.exists())
        self.transcribe_btn.setEnabled(has_video)

    # --- Project Management Slots ---

    @asyncSlot()  # type: ignore[misc]
    async def open_project(self) -> None:
        """Prompt the user to select and load an .asproj project file."""
        selected_path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "Auto-Subs Project (*.asproj)")
        if not selected_path:
            return

        path = Path(selected_path)
        self.statusBar().showMessage(f"Opening project {path.name}...")

        project_temp_dir = TEMP_DIR / f"project_{path.stem}_{uuid.uuid4().hex[:8]}"
        project_temp_dir.mkdir(parents=True, exist_ok=True)

        try:

            def _extract_and_find_files() -> tuple[Path, Path]:
                with zipfile.ZipFile(path, "r") as zf:
                    namelist = zf.namelist()
                    video_arcname = next((name for name in namelist if name.startswith("video.")), None)
                    if not video_arcname:
                        raise FileNotFoundError("Video file not found in project archive.")
                    if "project.json" not in namelist:
                        raise FileNotFoundError("'project.json' not found in project archive.")

                    zf.extractall(project_temp_dir)

                    return project_temp_dir / "project.json", project_temp_dir / video_arcname

            project_json_path, video_path_in_temp = await asyncio.to_thread(_extract_and_find_files)

            with open(project_json_path, encoding="utf-8") as f:
                project_data = json.load(f)

            style_data = project_data.get("style_data", {})
            subtitles_data = project_data.get("subtitles_data", {})

            self.video_manager.set_video_path(video_path_in_temp)
            self.style_manager.from_dict(style_data, notify_loaded=True)
            new_subtitles = await asyncio.to_thread(Subtitles.from_dict, subtitles_data)
            self.subtitles_manager.set_subtitles(new_subtitles)

            self._current_project_path = path
            self._update_window_title()
            self.statusBar().showMessage(f"Project '{path.name}' loaded successfully.", 5000)

        except (zipfile.BadZipFile, json.JSONDecodeError, ValueError, FileNotFoundError) as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load project:\n{str(e)}")
            self.statusBar().showMessage("Project load failed.", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"An unexpected error occurred while loading project:\n{str(e)}")
            self.statusBar().showMessage("Project load failed.", 5000)

    @asyncSlot()  # type: ignore[misc]
    async def save_project(self) -> None:
        """Save the current project to its existing path, or prompt for a new one."""
        if self._current_project_path:
            await self._save_to_path(self._current_project_path)
        else:
            await self.save_project_as()

    @asyncSlot()  # type: ignore[misc]
    async def save_project_as(self) -> None:
        """Prompt the user for a new path and save the project."""
        selected_path, _ = QFileDialog.getSaveFileName(self, "Save Project As", "", "Auto-Subs Project (*.asproj)")
        if not selected_path:
            return

        path = Path(selected_path)
        await self._save_to_path(path)
        self._current_project_path = path
        self._update_window_title()

    async def _save_to_path(self, path: Path) -> None:
        """Serialize the application state and write it to a compressed archive."""
        if not self.video_manager.video_path.exists():
            QMessageBox.warning(self, "Cannot Save", "A video must be loaded before saving a project.")
            return

        self.statusBar().showMessage(f"Saving project to {path.name}...")
        try:
            project_json_content = {
                "subtitles_data": self.subtitles_manager.subtitles.to_dict(),
                "style_data": self.style_manager.style,
            }
            video_source_path = self.video_manager.video_path

            def _create_archive() -> None:
                with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr("project.json", json.dumps(project_json_content, indent=2))
                    zf.write(video_source_path, arcname=f"video{video_source_path.suffix}")

            await asyncio.to_thread(_create_archive)
            self.statusBar().showMessage(f"Project saved to '{path.name}'.", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save project:\n{str(e)}")
            self.statusBar().showMessage("Project save failed.", 5000)

    def _update_window_title(self) -> None:
        """Update the main window title based on the current project path."""
        if self._current_project_path:
            self.setWindowTitle(f"Auto Subs - {self._current_project_path.name}")
        else:
            self.setWindowTitle("Auto Subs")

    # --- Menu Action Slots (Import/Export/Style) ---

    @asyncSlot()  # type: ignore[misc]
    async def import_mp4(self) -> None:
        """Prompt the user to select a video file to import."""
        selected_path, _ = QFileDialog.getOpenFileName(self, "Import Video", "", "Video files (*.mp4 *.mkv *.avi)")
        if selected_path:
            self._current_project_path = None
            self._update_window_title()
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
        selected_path, _ = QFileDialog.getSaveFileName(self, "Save Style As", str(STYLES_DIR), "JSON files (*.json)")
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
        selected_path, _ = QFileDialog.getOpenFileName(self, "Load Style", str(STYLES_DIR), "JSON files (*.json)")
        if selected_path:
            path = Path(selected_path)
            try:
                await asyncio.to_thread(self.style_manager.load_from_file, path)
                QMessageBox.information(self, "Style Loaded", f"Style loaded from:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Failed to load style:\n{str(e)}")
