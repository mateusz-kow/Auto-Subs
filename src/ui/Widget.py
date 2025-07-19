from enum import Enum
from typing import Any, Callable, Dict, List

from PySide6.QtWidgets import QWidget

# src/managers/BaseManager.py
from logging import getLogger
from typing import Callable, Generic, TypeVar

logger = getLogger(__name__)

# A generic type for the data that listeners will receive.
# For example, for SubtitlesManager, this would be `Subtitles`.
T = TypeVar("T")


class EventType(Enum):
    pass


class BaseManager(Generic[T]):
    """
    A generic base class for managers that handle state and notify listeners.

    This class provides a standardized, type-safe implementation for managing
    a list of listeners and notifying them of state changes.
    """

    def __init__(self) -> None:
        """Initialize the BaseManager with an empty list of listeners."""
        self._func_name_to_listeners: dict[EventType, list[Callable[[T], None]]] = {}

    def register_listener(self, anything: Any):
        for listener_type, listeners in self._func_name_to_listeners.items():
            func_name = listener_type.value
            if hasattr(anything, func_name):
                func = getattr(anything, func_name)
                listeners.append(func)

    def _notify_listeners(self, data: T, event_type: EventType) -> None:
        """
        Notify all registered listeners with the provided data.

        Args:
            data: The state data to pass to each listener.
        """
        listeners = self._func_name_to_listeners[event_type]
        logger.debug(f"Notifying {len(listeners)} listeners of change.")
        for listener in listeners:
            try:
                listener(data)
            except Exception as e:
                logger.exception(f"Listener {listener.__name__} raised an exception: {e}")


class Widget(QWidget):
    """
    Base class for all widgets in the application.
    Provides common functionality and properties that can be shared across different widgets.
    """

    def __init__(self, managers: list[Manager], parent: QWidget | None = None) -> None:
        """Initialize the Widget and connect to managers."""
        super().__init__(parent)
        for manager in managers:
            manager.connect(self)
