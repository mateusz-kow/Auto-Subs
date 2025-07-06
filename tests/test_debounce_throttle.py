import sys
from datetime import datetime

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from src.utils.QDebouncer import QDebouncer
from src.utils.QThrottler import QThrottler


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.debouncer = QDebouncer(1000)
        self.throttler = QThrottler(1000)
        self.index = 0

        self.label = QLabel("Press button")
        self.button = QPushButton("Press!")

        self.button.clicked.connect(self.on_button_click)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def on_button_click(self):
        self.debouncer.call(print, f"{self.index}. {datetime.now()}: Debounce: click!")
        self.throttler.call(print, f"{self.index}. {datetime.now()}: Throttle: click!")
        self.index += 1

    def update_label(self, text):
        self.label.setText(text)


# This is a simple PySide6 application to demonstrate the use of QDebouncer and QThrottler.
app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())
