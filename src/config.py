import tempfile
from pathlib import Path
from appdirs import user_data_dir, user_log_dir


# Metadata
APP_NAME = "auto-subs"
COMPANY_NAME = "mateusz-kow"
WHISPER_MODEL = "tiny"

# Paths
TEMP_DIR: Path = Path(tempfile.gettempdir()) / APP_NAME
LOCAL_DIR: Path = Path(user_data_dir(APP_NAME, COMPANY_NAME))
STYLES_DIR: Path = LOCAL_DIR / "Styles"
PROJECTS_DIR: Path = LOCAL_DIR / "Projects"
SETTINGS_DIR: Path = LOCAL_DIR / "Settings"
LOGS_DIR: Path = Path(user_log_dir(APP_NAME, COMPANY_NAME))

# Ensure required directories exist
REQUIRED_DIRS: list[Path] = [
    TEMP_DIR,
    LOCAL_DIR,
    STYLES_DIR,
    PROJECTS_DIR,
    SETTINGS_DIR,
    LOGS_DIR,
]

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "app.log",
            "maxBytes": 1 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "default",
            "level": "DEBUG",
            "encoding": "utf-8",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["file", "console"],
    },
}


try:
    from local_config import *
except ImportError:
    pass
