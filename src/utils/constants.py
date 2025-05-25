import tempfile
from pathlib import Path
from appdirs import user_data_dir
from typing import List
from src.utils.logger_config import get_logger
logger = get_logger(__name__)

# Application metadata
APP_NAME = "AutoSubs"
COMPANY_NAME = "GithubOzzy420"
WHISPER_MODEL = "tiny"

# Define paths
TEMP_DIR: Path = Path(tempfile.gettempdir()) / APP_NAME
LOCAL_DIR: Path = Path(user_data_dir(APP_NAME, COMPANY_NAME))
STYLES_DIR: Path = LOCAL_DIR / "Styles"
PROJECTS_DIR: Path = LOCAL_DIR / "Projects"
SETTINGS_DIR: Path = LOCAL_DIR / "Settings"

# Ensure required directories exist
REQUIRED_DIRS: List[Path] = [TEMP_DIR, LOCAL_DIR, STYLES_DIR, PROJECTS_DIR, SETTINGS_DIR]


def create_directories(dirs: List[Path]) -> None:
    """
    Ensure all specified directories exist. Create them if necessary.

    Args:
        dirs (List[Path]): List of Path objects representing directories to create.
    """
    for directory in dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ready: {directory}")
        except OSError:
            logger.exception(f"Failed to create directory: {directory}")
            raise


def clean_temp_dir() -> None:
    """
    Clean the temporary directory by removing all files and folders inside.

    Raises:
        OSError: If a file or folder cannot be removed.
    """
    try:
        for item in TEMP_DIR.iterdir():
            try:
                if item.is_dir():
                    item.rmdir()
                else:
                    item.unlink()
            except Exception as e:
                logger.warning(f"Could not delete {item}: {e}")
        logger.info(f"Temporary directory cleaned: {TEMP_DIR}")
    except OSError:
        logger.exception(f"Failed to clean temporary directory: {TEMP_DIR}")
        raise


# Initialize required folders at module load
create_directories(REQUIRED_DIRS)
