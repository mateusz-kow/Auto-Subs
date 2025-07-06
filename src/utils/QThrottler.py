from PySide6.QtCore import QDateTime, QObject, QTimer


class QThrottler(QObject):
    """
    A utility class to throttle the execution of a function, ensuring it is not called
    more frequently than the specified interval. If a call is made during the interval,
    it will be queued and executed after the interval has elapsed.

    Attributes:
        interval (int): The minimum interval (in milliseconds) between function calls.
    """

    def __init__(self, interval_ms: int):
        """
        Initialize the QThrottler.

        Args:
            interval_ms (int): The minimum interval (in milliseconds) between function calls.
        """
        super().__init__()
        self.interval = interval_ms
        self._last_call_time: int = 0
        self._trailing_timer: QTimer = QTimer(self)
        self._trailing_timer.setSingleShot(True)
        self._pending_func: callable = None
        self._pending_args: tuple = ()
        self._pending_kwargs: dict = {}

    def call(self, func: callable, *args, **kwargs) -> None:
        """
        Call the given function, ensuring it adheres to the throttling interval.

        Args:
            func (callable): The function to be called.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        """
        now = QDateTime.currentMSecsSinceEpoch()
        elapsed = now - self._last_call_time

        if elapsed >= self.interval:
            self._last_call_time = now
            func(*args, **kwargs)
        else:
            # Save the last call as pending
            self._pending_func = func
            self._pending_args = args
            self._pending_kwargs = kwargs

            if not self._trailing_timer.isActive():
                remaining = self.interval - elapsed
                self._trailing_timer.timeout.connect(self._trigger_pending)
                self._trailing_timer.start(remaining)

    def _trigger_pending(self) -> None:
        """Trigger the pending function call, if any, and reset the pending state."""
        if self._pending_func:
            self._last_call_time = QDateTime.currentMSecsSinceEpoch()
            self._pending_func(*self._pending_args, **self._pending_kwargs)
            self._pending_func = None
