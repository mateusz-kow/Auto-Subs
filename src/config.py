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

# Default style configuration
DEFAULT_STYLE = {
    "title": "Default",
    "font": "Comic Sans MS",
    "font_size": 80,
    "primary_color": "&H00FFAAFF",
    "secondary_color": "&H00000000",
    "outline_color": "&H005D3E5D",
    "back_color": "&H00442E44",
    "bold": -1,
    "italic": 0,
    "underline": 0,
    "strikeout": 0,
    "scale_x": 100,
    "scale_y": 100,
    "spacing_spinbox": 0.0,
    "angle": 0,
    "border_style": 1,
    "outline": 8,
    "shadow": 10,
    "alignment": 2,
    "margin_l": 10,
    "margin_r": 10,
    "margin_v": 350,
    "encoding": 0,
    "play_res_x": 1920,
    "play_res_y": 1080,
    "wrap_style": 0,
    "scaled_border_and_shadow": "yes",
    "highlight_style": {
        "text_color": "&H00FFFF55",
        "border_color": "&H00353512",
        "fade": False,
    },
}


# Overwrite with local configuration if available
try:  # noqa: SIM105
    from local_config import *  # noqa: F403
except ImportError:
    pass
