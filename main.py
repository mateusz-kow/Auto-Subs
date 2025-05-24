import sys
import asyncio
from asyncio import all_tasks

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
from src.utils.constants import clean_temp_dir
from src.ui.SubtitleEditorApp import SubtitleEditorApp


def main() -> None:
    """
    Entry point for the Subtitle Editor application.
    Sets up the QApplication, integrates the asyncio event loop with Qt,
    and starts the main application window.
    """
    # Create the Qt application
    app = QApplication(sys.argv)

    # Integrate the asyncio event loop with Qt
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Initialize the main application window
    window = SubtitleEditorApp()
    window.resize(900, 600)
    window.show()

    try:
        # Run the event loop
        with loop:
            loop.run_forever()
    except KeyboardInterrupt:
        print("Application interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        tasks = [t for t in all_tasks(loop) if not t.done()]
        if tasks:
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()
        clean_temp_dir()


if __name__ == "__main__":
    main()
