from enum import Enum
from logging import getLogger
from typing import Any, Callable, Generic, TypeVar

logger = getLogger(__name__)

# A generic type for the data that listeners will receive.
T = TypeVar("T")


class EventType(Enum):
    """Base class for event type enumerations."""

    pass


class BaseManager(Generic[T]):
    """A generic base class for managers that handle state and notify listeners.

    This class provides a standardized, type-safe implementation for managing
    a list of listeners and notifying them of state changes.
    """

    def __init__(self, event_types_enum: type[EventType]) -> None:
        """Initialize the BaseManager.

        Args:
            event_types_enum: The Enum class defining the events for this manager.
        """
        self._event_types_enum = event_types_enum
        self._listeners: dict[EventType, list[Callable[[Any], None]]] = {
            event_type: [] for event_type in self._event_types_enum
        }

    def register_listener(self, listener_obj: Any) -> None:
        """Register a listener object.

        This method inspects the listener object for methods that match the
        names defined in the manager's EventType enum and registers them.

        Args:
            listener_obj: The object to register as a listener.
        """
        for event_type, methods in self._listeners.items():
            method_name = event_type.value
            if hasattr(listener_obj, method_name):
                method = getattr(listener_obj, method_name)
                if callable(method):
                    methods.append(method)

    def _notify_listeners(self, data: T, event_type: EventType) -> None:
        """Notify all registered listeners for a specific event type.

        Args:
            data: The state data to pass to each listener.
            event_type: The specific event that occurred.
        """
        if event_type not in self._listeners:
            raise NotImplementedError(f"Event type {event_type} not implemented for {self.__class__.__name__}")

        logger.debug(f"Notifying {len(self._listeners[event_type])} listeners for {event_type.name}.")
        for listener in self._listeners[event_type]:
            try:
                listener(data)
            except Exception:
                logger.exception(f"Listener {getattr(listener, '__name__', 'unknown')} raised an exception")
