# src/managers/style_manager.py
import json
import os
from logging import getLogger
from pathlib import Path
from typing import Any

from src.config import DEFAULT_STYLE
from src.managers.base_manager import BaseManager, EventType
from src.utils.QThrottler import QThrottler

logger = getLogger(__name__)


class StyleEventType(EventType):
    """Defines the event types for the StyleManager."""

    STYLE_CHANGED = "on_style_changed"
    STYLE_LOADED = "on_style_loaded"


class StyleManager(BaseManager[dict[str, Any]]):
    """Class for managing subtitle styles and related file operations."""

    def __init__(self) -> None:
        """Initialize the StyleManager with default values."""
        super().__init__(StyleEventType)
        self._style = DEFAULT_STYLE.copy()

        self._style_changed_throttler = QThrottler(1000)
        self._style_loaded_throttler = QThrottler(1000)

    def from_dict(self, new_style: dict[str, Any], notify_loaded: bool = False) -> None:
        """
        Update the current style with a new style dictionary and notify listeners.

        Args:
            new_style (dict): A dictionary containing the new style values.
            notify_loaded (bool): If True, also notify style_loaded_listeners.
        """
        if new_style == self._style or new_style is None:
            return

        logger.debug(f"Updating style: {new_style}")
        self._style.update(new_style)

        self._style_changed_throttler.call(self._notify_listeners, self._style, StyleEventType.STYLE_CHANGED)

        if notify_loaded:
            self._style_loaded_throttler.call(self._notify_listeners, self._style, StyleEventType.STYLE_LOADED)

    def reset_to_default(self) -> None:
        """Reset the style to the default values and notify listeners."""
        logger.debug("Resetting style to default")
        self.from_dict(DEFAULT_STYLE.copy(), notify_loaded=True)

    def save_to_file(self, path: Path) -> Path:
        """
        Save the current style to a JSON file.

        Args:
            path (Optional[str]): The file path where the style should be saved. Defaults to the style title.

        Returns:
            str: The path where the style was saved.
        """
        if path is None:
            filename = f"{self._style['title']}.json"
            path = Path(os.path.abspath(filename))

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._style, f, indent=2)
            logger.info(f"Style saved to {path}")
        except OSError as e:
            logger.error(f"Failed to save style to {path}: {e}")
            raise

        return path

    def load_from_file(self, path: Path) -> None:
        """
        Load style from a JSON file.

        Args:
            path (str): The file path from which to load the style.
        """
        path = path.absolute()
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            data = DEFAULT_STYLE | data  # Merge with default style
            if data == self._style or data is None:
                return

            logger.debug(f"Loaded style from {path}: {data}")
            self.from_dict(data, notify_loaded=True)
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load style from {path}: {e}")
            raise

    @property
    def style(self) -> dict[str, Any]:
        """Return the current style dictionary."""
        return self._style
