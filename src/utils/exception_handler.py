import sys
import traceback
from logging import getLogger
from types import TracebackType

from PySide6.QtWidgets import QMessageBox

logger = getLogger(__name__)


def global_exception_handler(exctype: type[BaseException], value: BaseException, tb: TracebackType | None) -> None:
    """
    A global exception handler to catch unhandled exceptions, log them,
    and display a user-friendly error message in a QMessageBox.

    This function is designed to be set as sys.excepthook.

    Args:
        exctype: The type of the exception (e.g., ValueError).
        value: The exception instance itself.
        tb: A traceback object, which may be None.
    """
    # Format the traceback into a string. The traceback module handles tb being None.
    traceback_details: str = "".join(traceback.format_exception(exctype, value, tb))

    # Log the critical error using the existing logging configuration
    error_message: str = f"An unhandled exception occurred:\n{traceback_details}"
    logger.critical(error_message)

    # Create a user-friendly error message box
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.setWindowTitle(exctype.__name__)
    msg_box.setText(str(value) if str(value) else "An unexpected error occurred. Please check the logs for details.")

    # The setDetailedText allows the user to see the full technical error if they choose
    msg_box.setDetailedText(traceback_details)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

    msg_box.exec()


def install_handler() -> None:
    """Installs the global exception handler by setting sys.excepthook."""
    sys.excepthook = global_exception_handler
    logger.info("Global exception handler installed.")
