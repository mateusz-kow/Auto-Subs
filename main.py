import sys
import asyncio

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from src.utils.constants import clean_temp_dir
from ui.SubtitleEditorApp import SubtitleEditorApp


def main():
    app = QApplication(sys.argv)

    # Integrate asyncio event loop with Qt
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = SubtitleEditorApp()
    window.resize(1100, 700)
    window.show()

    try:
        with loop:
            loop.run_forever()
    except KeyboardInterrupt:
        print("Application interrupted by user.")
    finally:
        loop.close()
        clean_temp_dir()


if __name__ == "__main__":
    main()
#
# New style: {'title': 'Default',
#             'font': 'Segoe UI',
#             'font_size': 56,
#             'bold': -1,
#             'italic': 0, 'primary_color': '&H00FFFFFF',
#             'alignment': 2, 'margin_l': 10, 'margin_r': 10, 'margin_v': 500, 'border_style': 1,
#             'outline': 8, 'shadow': 0, 'encoding': 0, 'highlight_style': '{\\1c&H99CCFF\\3c&H000000}'}
