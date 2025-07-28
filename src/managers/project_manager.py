import asyncio
import json
import uuid
import zipfile
from logging import getLogger
from pathlib import Path
from typing import Any

from src.config import TEMP_DIR
from src.managers.base_manager import BaseManager, EventType
from src.managers.style_manager import StyleManager
from src.managers.subtitles_manager import SubtitlesManager
from src.managers.video_manager import VideoManager
from src.subtitles.models import Subtitles

logger = getLogger(__name__)


class ProjectEventType(EventType):
    """Defines the event types for the ProjectManager."""

    PROJECT_OPENED = "on_project_opened"
    PROJECT_SAVED = "on_project_saved"
    PROJECT_CLOSED = "on_project_closed"
    PROJECT_LOAD_FAILED = "on_project_load_failed"
    PROJECT_SAVE_FAILED = "on_project_save_failed"


class ProjectManager(BaseManager[Any]):
    """Manages project state, including loading and saving .asproj files."""

    def __init__(
        self,
        video_manager: VideoManager,
        subtitles_manager: SubtitlesManager,
        style_manager: StyleManager,
    ) -> None:
        """Initialize the ProjectManager.

        Args:
            video_manager: The manager for video state.
            subtitles_manager: The manager for subtitle data.
            style_manager: The manager for style data.
        """
        super().__init__(ProjectEventType)
        self._video_manager = video_manager
        self._subtitles_manager = subtitles_manager
        self._style_manager = style_manager
        self._current_project_path: Path | None = None

    @property
    def current_project_path(self) -> Path | None:
        """Get the path of the currently open project."""
        return self._current_project_path

    async def open_project(self, path: Path) -> None:
        """Load a project from a .asproj file.

        This method unzips the project file, loads the video and project data,
        updates the relevant managers, and notifies listeners of the outcome.

        Args:
            path: The file path to the .asproj project file.
        """
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

            self._video_manager.set_video_path(video_path_in_temp)
            self._style_manager.from_dict(style_data, notify_loaded=True)
            new_subtitles = await asyncio.to_thread(Subtitles.from_dict, subtitles_data)
            self._subtitles_manager.set_subtitles(new_subtitles)

            self._current_project_path = path
            self._notify_listeners(path, ProjectEventType.PROJECT_OPENED)

        except (zipfile.BadZipFile, json.JSONDecodeError, ValueError, FileNotFoundError) as e:
            logger.error(f"Failed to load project from {path}: {e}")
            self._notify_listeners(e, ProjectEventType.PROJECT_LOAD_FAILED)
        except Exception as e:
            logger.exception(f"An unexpected error occurred while loading project from {path}: {e}")
            self._notify_listeners(e, ProjectEventType.PROJECT_LOAD_FAILED)

    async def save_project(self) -> None:
        """Save the current project to its existing path."""
        if self._current_project_path:
            await self._save_to_path(self._current_project_path)
        else:
            error = ValueError("No project path is set. Cannot save.")
            self._notify_listeners(error, ProjectEventType.PROJECT_SAVE_FAILED)

    async def save_project_as(self, path: Path) -> None:
        """Save the current project to a new specified path."""
        await self._save_to_path(path)

    async def _save_to_path(self, path: Path) -> None:
        """Serialize the application state and write it to a compressed .asproj archive.

        Args:
            path: The file path where the project will be saved.
        """
        if not self._video_manager.video_path.exists():
            error = ValueError("A video must be loaded before saving a project.")
            self._notify_listeners(error, ProjectEventType.PROJECT_SAVE_FAILED)
            return

        try:
            project_json_content = {
                "subtitles_data": self._subtitles_manager.subtitles.to_dict(),
                "style_data": self._style_manager.style,
            }
            video_source_path = self._video_manager.video_path

            def _create_archive() -> None:
                with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr("project.json", json.dumps(project_json_content, indent=2))
                    zf.write(video_source_path, arcname=f"video{video_source_path.suffix}")

            await asyncio.to_thread(_create_archive)
            self._current_project_path = path
            self._notify_listeners(path, ProjectEventType.PROJECT_SAVED)
        except Exception as e:
            logger.exception(f"Failed to save project to {path}: {e}")
            self._notify_listeners(e, ProjectEventType.PROJECT_SAVE_FAILED)

    def close_project(self) -> None:
        """Close the current project, resetting the path and notifying listeners."""
        if self._current_project_path:
            logger.info(f"Closing project: {self._current_project_path.name}")
            self._current_project_path = None
            self._notify_listeners(None, ProjectEventType.PROJECT_CLOSED)
