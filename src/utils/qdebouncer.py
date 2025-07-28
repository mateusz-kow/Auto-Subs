from typing import Any, Callable

from PySide6.QtCore import QObject, QTimer


class QDebouncer(QObject):
    """A utility class to debounce function calls, ensuring that the function is only executed
    after a specified delay has passed since the last call.
    """

    def __init__(self, delay_ms: int):
        """Initialize the QDebouncer.

        Args:
            delay_ms (int): The debounce delay in milliseconds.
        """
        super().__init__()
        self.delay: int = delay_ms
        self.timer: QTimer = QTimer(self)
        self.timer.setSingleShot(True)

        self._callback: Callable[..., Any] | None = None
        self._args: tuple[Any, ...] = ()
        self._kwargs: dict[str, Any] = {}

        self.timer.timeout.connect(self._trigger)

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Schedule a function to be called after the debounce delay.

        Args:
            func (Callable): The function to debounce.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.
        """
        self._callback = func
        self._args = args
        self._kwargs = kwargs

        if self.timer.isActive():
            self.timer.stop()
        self.timer.start(self.delay)

    def _trigger(self) -> None:
        """Execute the debounced function with the stored arguments."""
        if self._callback:
            self._callback(*self._args, **self._kwargs)
