import sys
import asyncio
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
from src.utils.constants import clean_temp_dir
from ui.SubtitleEditorApp import SubtitleEditorApp


def main():
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
    window.resize(1100, 700)
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
        # Ensure the event loop is closed and temporary files are cleaned up
        loop.close()
        clean_temp_dir()


if __name__ == "__main__":
    main()
