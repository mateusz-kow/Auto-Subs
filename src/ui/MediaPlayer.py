import vlc
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtCore import QTimer


class MediaPlayer(QWidget):
    """A QWidget that encapsulates VLC media player functionality."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")  # Set background for the video area

        # Create VLC instance and media player
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # Create a QLabel for displaying an image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")  # Match the background color

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.addWidget(self.image_label)  # Add the QLabel to the layout
        self.setLayout(layout)

        # Set the video output to this widget
        self.media_player.set_hwnd(self.winId())  # For Windows

        # Listeners for video percent changes
        self.video_percent_changed_listeners = []

        # Timer to track playback progress
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self._check_progress)
        self.progress_timer.start(500)  # Check every 500ms

    def set_media(self, file_path: str):
        """Set the media file to play."""
        media = self.instance.media_new(file_path)
        self.media_player.set_media(media)
        self.play()
        self.pause()

    def set_image(self, image_path: str):
        """Set an image to display."""
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.show()  # Show the image

    def play(self):
        """Play the media."""
        self.image_label.hide()  # Hide the image when playing
        self.media_player.play()

    def pause(self):
        """Pause the media."""
        self.media_player.pause()

    def stop(self):
        """Stop the media."""
        self.media_player.stop()
        self.image_label.show()  # Show the image when stopped

    def set_timestamp(self, timestamp: float):
        """Set the playback position to the given timestamp (in milliseconds)."""
        self.media_player.set_time(int(timestamp * 1000))

    def add_video_percent_changed_listener(self, listener):
        """Add a listener for video percent changes."""
        self.video_percent_changed_listeners.append(listener)

    def _check_progress(self):
        """Check the playback progress and notify listeners."""
        if self.media_player.is_playing():
            total_time = self.media_player.get_length()  # Total duration in milliseconds
            current_time = self.media_player.get_time()  # Current time in milliseconds
            if total_time > 0:
                percent = (current_time / total_time) * 100
                for listener in self.video_percent_changed_listeners:
                    listener(percent)