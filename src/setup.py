from src.config import REQUIRED_DIRS, LOGGING_CONFIG
from logging.config import dictConfig


def setup_project() -> None:
    """
    Set up the project by ensuring all required directories exist and initializing logging.
    """
    # Ensure all required directories exist
    for directory in REQUIRED_DIRS:
        directory.mkdir(parents=True, exist_ok=True)

    # Initialize logging configuration
    dictConfig(LOGGING_CONFIG)
