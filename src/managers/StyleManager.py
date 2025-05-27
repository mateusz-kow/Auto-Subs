import json
import os

from typing import Callable, Optional

from src.utils.QThrottler import QThrottler

from logging import getLogger
logger = getLogger(__name__)

DEFAULT_STYLE = {
    "title": "Default",
    "font": "Comic Sans MS",
    "font_size": 80,
    "primary_color": "&H00FFAAFF",
    "secondary_color": "&H00000000",
    "outline_color": "&H005D3E5D",
    "back_color": "&H00442E44",
    "bold": -1,
    "italic": 0,
    "underline": 0,
    "strikeout": 0,
    "scale_x": 100,
    "scale_y": 100,
    "spacing_spinbox": 0.0,
    "angle": 0,
    "border_style": 1,
    "outline": 8,
    "shadow": 10,
    "alignment": 2,
    "margin_l": 10,
    "margin_r": 10,
    "margin_v": 350,
    "encoding": 0,
    "play_res_x": 1920,
    "play_res_y": 1080,
    "wrap_style": 0,
    "scaled_border_and_shadow": "yes",
    "highlight_style": {
        "text_color": "&H00FFFF55",
        "border_color": "&H00353512",
        "fade": False
    }
}


class StyleManager:
    """Class for managing subtitle styles and related file operations."""

    def __init__(self):
        """Initialize the StyleManager with default values."""
        self._style = DEFAULT_STYLE.copy()
        self._style_listeners = []
        self._style_loaded_listeners = []
        self._style_throttler = QThrottler(1000)
        self._style_loaded_throttler = QThrottler(1000)

    def from_dict(self, new_style: dict):
        """
        Update the current style with a new style dictionary and notify listeners.

        Args:
            new_style (dict): A dictionary containing the new style values.
        """
        if new_style == self._style or new_style is None:
            return

        logger.debug(f"Updating style: {new_style}")
        self._style.update(new_style)

        self._style_throttler.call(self._notify_style_listeners, self._style)

    def _notify_style_listeners(self, new_style: dict):
        """
        Notify all registered style listeners with the new style.

        Args:
            new_style (dict): The new style to notify listeners with.
        """
        for listener in self._style_listeners:
            listener(new_style)

    def reset_to_default(self):
        """Reset the style to the default values and notify listeners."""
        logger.debug("Resetting style to default")
        self.from_dict(DEFAULT_STYLE.copy())

    def save_to_file(self, path: Optional[str] = None) -> str:
        """
        Save the current style to a JSON file.

        Args:
            path (Optional[str]): The file path where the style should be saved. Defaults to the style title.

        Returns:
            str: The path where the style was saved.
        """
        if path is None:
            filename = f"{self._style['title']}.json"
            path = os.path.abspath(filename)

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._style, f, indent=2)
            logger.info(f"Style saved to {path}")
        except IOError as e:
            logger.error(f"Failed to save style to {path}: {e}")
            raise

        return path

    def load_from_file(self, path: str):
        """
        Load style from a JSON file.

        Args:
            path (str): The file path from which to load the style.
        """
        path = os.path.abspath(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            data = DEFAULT_STYLE | data  # Merge with default style
            if data == self._style or data is None:
                return

            logger.debug(f"Loaded style from {path}: {data}")
            self.from_dict(data)

            self._style_loaded_throttler.call(self._notify_style_loaded_listeners, data)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load style from {path}: {e}")
            raise

    def _notify_style_loaded_listeners(self, new_style: dict):
        """
        Notify all registered style loaded listeners with the new style.

        Args:
            new_style (dict): The new style to notify listeners with.
        """
        for listener in self._style_loaded_listeners:
            listener(new_style)

    def add_style_listener(self, listener: Callable):
        """
        Add a listener that will be called when the style is updated.

        Args:
            listener (Callable): The listener function to be added.
        """
        if listener not in self._style_listeners:
            self._style_listeners.append(listener)
            logger.debug(f"Added style listener: {listener}")
        else:
            logger.warning("Listener already exists")

    def add_style_loaded_listener(self, listener: Callable):
        """
        Add a listener that will be called after the style is loaded.

        Args:
            listener (Callable): The listener function to be added.
        """
        if listener not in self._style_loaded_listeners:
            self._style_loaded_listeners.append(listener)
            logger.debug(f"Added style loaded listener: {listener}")
        else:
            logger.warning("Listener already exists")

    @property
    def style(self):
        return self._style
