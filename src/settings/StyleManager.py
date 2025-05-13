import json
import os
import logging
from typing import Callable, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_STYLE = {
    'title': 'Untitled',
    'font': 'Arial',
    'font_size': 75,
    'primary_color': '&H00FFFFFF',
    'secondary_color': '&H000000FF',
    'outline_color': '&H00000000',
    'back_color': '&H64000000',
    'bold': 0,
    'italic': 0,
    'underline': 0,
    'strikeout': 0,
    'scale_x': 100,
    'scale_y': 100,
    'spacing_spinbox': 0,
    'angle': 0,
    'border_style': 1,
    'outline': 1,
    'shadow': 0,
    'alignment': 2,
    'margin_l': 10,
    'margin_r': 10,
    'margin_v': 500,
    'encoding': 1,
    'play_res_x': 1920,
    'play_res_y': 1080,
    'wrap_style': 0,
    'scaled_border_and_shadow': 'yes'
}


class StyleManager:
    """Singleton class for managing subtitle styles and related file operations."""

    _instance: Optional["StyleManager"] = None
    _style: dict
    _style_listeners: list[Callable]
    _style_loaded_listeners: list[Callable]

    def __new__(cls) -> "StyleManager":
        """Ensure that there is only one instance of StyleManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._style = DEFAULT_STYLE.copy()
            cls._instance._style_listeners = []
            cls._instance._style_loaded_listeners = []
        return cls._instance

    def to_dict(self) -> dict:
        """
        Get the current style as a dictionary.

        Returns:
            dict: The current style configuration.
        """
        return self._style

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

            data = DEFAULT_STYLE | data   # Merge with default style
            if data == self._style or data is None:
                return

            logger.debug(f"Loaded style from {path}: {data}")
            self.from_dict(data)

            for listener in self._style_loaded_listeners:
                listener(data)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load style from {path}: {e}")
            raise

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

    def remove_style_listener(self, listener: Callable):
        """
        Remove a listener that was previously added.

        Args:
            listener (Callable): The listener function to be removed.
        """
        if listener in self._style_listeners:
            self._style_listeners.remove(listener)
            logger.debug(f"Removed style listener: {listener}")
        else:
            logger.warning("Listener not found")

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

    def remove_style_loaded_listener(self, listener: Callable):
        """
        Remove a listener that was previously added after the style is loaded.

        Args:
            listener (Callable): The listener function to be removed.
        """
        if listener in self._style_loaded_listeners:
            self._style_loaded_listeners.remove(listener)
            logger.debug(f"Removed style loaded listener: {listener}")
        else:
            logger.warning("Listener not found")

