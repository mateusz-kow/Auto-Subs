# src/managers/video_manager.py
from logging import getLogger
from pathlib import Path

from src.managers.base_manager import BaseManager, EventType
from src.utils.ffmpeg_utils import get_video_duration

logger = getLogger(__name__)


class VideoEventType(EventType):
    """Defines the event types for the VideoManager."""

    VIDEO_CHANGED = "on_video_changed"


class VideoManager(BaseManager[Path]):
    """Manages video-related operations, including setting the video path
    and notifying listeners when the video changes.
    """

    def __init__(self, video_path: Path | None = None) -> None:
        """Initialize the VideoManager.

        Args:
            video_path (Path, optional): The initial path to the video. Defaults to None.
        """
        super().__init__(VideoEventType)

        self._video_duration: float = 0.0
        self._video_path: Path = video_path if video_path is not None else Path()

        logger.info(f"VideoManager initialized with video path: {video_path}")

    def set_video_path(self, path: Path) -> None:
        """Set the path to the video and notify all registered listeners.

        Args:
            path (Path): The new video path.
        """
        if not isinstance(path, Path):
            raise ValueError("The video path must be a Path object.")

        self._video_path = path
        self._video_duration = get_video_duration(str(path))
        logger.info("Video path set to: %s, Duration: %.2f seconds", path, self._video_duration)

        self._notify_listeners(path, VideoEventType.VIDEO_CHANGED)

    @property
    def video_path(self) -> Path:
        """Get the current video path."""
        return self._video_path

    @property
    def video_duration(self) -> float:
        """Get the duration of the current video in seconds."""
        return self._video_duration
