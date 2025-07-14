from logging import getLogger
from pathlib import Path
from typing import Any, Callable, Union

from src.utils.ffmpeg_utils import get_video_duration

logger = getLogger(__name__)


class VideoManager:
    """
    Manages video-related operations, including setting the video path
    and notifying listeners when the video changes.
    """

    def __init__(self, video_path: Union[Path, None] = None) -> None:
        """
        Initialize the VideoManager.

        Args:
            video_path (Path, optional): The initial path to the video. Defaults to None.
        """
        self._video_duration: float = 0.0
        self._video_path: Path = video_path if video_path is not None else Path()
        self._video_changed_listeners: list[Callable[[Path], Any]] = []

        logger.info("VideoManager initialized with video path: %s", video_path)

    def set_video_path(self, path: Path) -> None:
        """
        Set the path to the video and notify all registered listeners.

        Args:
            path (Path): The new video path.
        """
        if not isinstance(path, Path):
            raise ValueError("The video path must be a Path object.")

        self._video_path = path
        self._video_duration = get_video_duration(str(path))  # Ensure it's passed as str
        logger.info("Video path set to: %s, Duration: %.2f seconds", path, self._video_duration)

        for listener in self._video_changed_listeners:
            listener(path)

    def add_video_listener(self, listener: Callable[[Path], Any]) -> None:
        """
        Register a listener to be notified when the video path changes.

        Args:
            listener (Callable[[Path], Any]): A function to be called when the video path changes.
        """
        if not callable(listener):
            raise ValueError("The listener must be callable.")

        if listener not in self._video_changed_listeners:
            self._video_changed_listeners.append(listener)
        else:
            raise ValueError("The listener is already registered.")

    @property
    def video_path(self) -> Path:
        """Get the current video path."""
        return self._video_path

    @property
    def video_duration(self) -> float:
        """Get the duration of the current video in seconds."""
        return self._video_duration
