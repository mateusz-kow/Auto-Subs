import sys
import vlc
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QFileDialog

# Initialize VLC instance
instance = vlc.Instance()
class VLCPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VLC Video Player")
        self.setGeometry(100, 100, 800, 600)

        # Create VLC instance and media player
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # Create GUI elements
        self.video_frame = QWidget(self)
        self.video_frame.setStyleSheet("background-color: black;")
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.open_button = QPushButton("Open File")

        # Connect buttons to their respective functions
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        self.stop_button.clicked.connect(self.stop_video)
        self.open_button.clicked.connect(self.open_file)

        # Layout for controls and video
        layout = QVBoxLayout()
        layout.addWidget(self.video_frame)
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
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
        if file_path:
            media = self.instance.media_new(file_path)
            self.media_player.set_media(media)
            self.media_player.set_hwnd(self.video_frame.winId())  # Set the video output to the QWidget
            self.play_video()

    def play_video(self):
        """Play the video."""
        if self.media_player.get_media():
            self.media_player.play()

    def pause_video(self):
        """Pause the video."""
        self.media_player.pause()

    def stop_video(self):
        """Stop the video."""
        self.media_player.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VLCPlayer()
    player.show()
    sys.exit(app.exec())