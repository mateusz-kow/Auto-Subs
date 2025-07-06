from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMainWindow,
    QPushButton,
    QFileDialog,
)
import sys
from PySide6.QtWidgets import QApplication
from src.ui.MediaPlayer import MediaPlayer


class VLCPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VLC Video Player")
        self.setGeometry(100, 100, 800, 600)

        # Create an instance of VLCMediaPlayer
        self.video_widget = MediaPlayer(self)

        # Create GUI elements
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.open_button = QPushButton("Open File")

        # Connect buttons to their respective functions
        self.play_button.clicked.connect(self.video_widget.play)
        self.pause_button.clicked.connect(self.video_widget.pause)
        self.stop_button.clicked.connect(self.video_widget.stop)
        self.open_button.clicked.connect(self.open_file)

        # Layout for controls and video
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addWidget(self.open_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.stop_button)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_file(self):
        """Open a video file and set it to the VLC media player."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)"
        )
        if file_path:
            self.video_widget.set_media(file_path)
            self.video_widget.play()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VLCPlayer()
    player.show()
    sys.exit(app.exec())
