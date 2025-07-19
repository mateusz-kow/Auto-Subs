import asyncio
import sys
from asyncio import all_tasks
from logging import getLogger

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from src.config import TEMP_DIR
from src.setup import setup_project
from src.ui.subtitle_editor_app import SubtitleEditorApp
from src.utils.exception_handler import install_handler

logger = getLogger(__name__)


def clean_temp_dir() -> None:
    """Clean the temporary directory by removing all files and folders inside.

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


def main() -> None:
    """Entry point for the Subtitle Editor application.
    Sets up the QApplication, integrates the asyncio event loop with Qt,
    and starts the main application window.
    """
    # Set up the project environment
    setup_project()

    # Create the Qt application
    logger.debug("Initializing application")
    app = QApplication(sys.argv)

    install_handler()

    # Integrate the asyncio event loop with Qt
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Initialize the main application window
    window = SubtitleEditorApp()
    window.resize(900, 600)
    window.show()
    logger.debug("Application initialized.")

    try:
        # Run the event loop
        with loop:
            loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
    except Exception:
        logger.exception("An unexpected error occurred")
    finally:
        tasks = [t for t in all_tasks(loop) if not t.done()]
        if tasks:
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()
        clean_temp_dir()
        logger.info("Application closed.")


if __name__ == "__main__":
    main()
