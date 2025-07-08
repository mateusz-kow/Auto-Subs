from logging import getLogger

from src.utils.ffmpeg_utils import get_video_duration

logger = getLogger(__name__)


class VideoManager:
    """
    Manages video-related operations, including setting the video path
    and notifying listeners when the video changes.
    """

    def __init__(self, video_path: str = None):
        """
        Initialize the VideoManager.

        Args:
            video_path (str, optional): The initial path to the video. Defaults to None.
        """
        self._video_duration: float = 0.0
        self._video_path: str = video_path
        self._video_changed_listeners: list[callable] = []
        logger.info("VideoManager initialized with video path: %s", video_path)

    def set_video_path(self, path: str) -> None:
        """
        Set the path to the video and notify all registered listeners.

        Args:
            path (str): The new video path.
        """
        if not isinstance(path, str):
            raise ValueError("The video path must be a string.")

        self._video_path = path
        self._video_duration = get_video_duration(path)
        logger.info(f"Video path set to: {path}, Duration: {self._video_duration} seconds")
        for listener in self._video_changed_listeners:
            listener(path)

    def add_video_listener(self, listener: callable) -> None:
        """
        Register a listener to be notified when the video path changes.

        Args:
            listener (callable): A function to be called when the video path changes.
        """
        if not callable(listener):
            raise ValueError("The listener must be a callable.")

        if listener not in self._video_changed_listeners:
            self._video_changed_listeners.append(listener)
        else:
            raise ValueError("The listener is already registered.")

    @property
    def video_path(self):
        return self._video_path
