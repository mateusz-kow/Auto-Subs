import logging
import sys


def get_logger(name: str = "global_logger") -> logging.Logger:
    """
    Configure and return a logger instance with standardized formatting.

    Args:
        name (str): Name of the logger. Defaults to "global_logger".

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Change to INFO or WARNING in production

    if not logger.hasHandlers():
        # Formatter: includes timestamp, log level, filename, line number, and message
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Optional: enable file logging
        # file_handler = logging.FileHandler("app.log")
        # file_handler.setFormatter(formatter)
        # logger.addHandler(file_handler)

        logger.propagate = False  # Prevent duplicate logs in some environments

    return logger
