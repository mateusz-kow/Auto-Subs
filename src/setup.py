from logging.config import dictConfig

from src.config import LOGGING_CONFIG, REQUIRED_DIRS


def setup_project() -> None:
    """
    Set up the project by ensuring all required directories exist and initializing logging.
    """
    # Ensure all required directories exist
    for directory in REQUIRED_DIRS:
        directory.mkdir(parents=True, exist_ok=True)

    # Initialize logging configuration
    dictConfig(LOGGING_CONFIG)
