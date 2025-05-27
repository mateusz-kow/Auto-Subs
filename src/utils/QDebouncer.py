from PySide6.QtCore import QTimer, QObject


class QDebouncer(QObject):
    """
    A utility class to debounce function calls, ensuring that the function is only executed
    after a specified delay has passed since the last call.

    Attributes:
        delay (int): The debounce delay in milliseconds.
    """

    def __init__(self, delay_ms: int):
        """
        Initialize the QDebouncer.

        Args:
            delay_ms (int): The debounce delay in milliseconds.
        """
        super().__init__()
        self.delay: int = delay_ms
        self.timer: QTimer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._trigger)
        self._func: callable = None
        self._args: tuple = ()
        self._kwargs: dict = {}

    def call(self, func: callable, *args, **kwargs) -> None:
        """
        Schedule a function to be called after the debounce delay.

        If the function is called again before the delay has elapsed, the timer is reset.

        Args:
            func (callable): The function to be debounced.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        """
        self._func = func
        self._args = args
        self._kwargs = kwargs
        if self.timer.isActive():
            self.timer.stop()
        self.timer.start(self.delay)

    def _trigger(self) -> None:
        """
        Execute the debounced function with the stored arguments.
        """
        if self._func:
            self._func(*self._args, **self._kwargs)
