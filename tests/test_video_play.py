import os

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import vlc
import sys

vlc_path = r"C:\Users\mw-ko\PycharmProjects\Auto-Subs\.venv\Lib\site-packages\vlc.py"
os.add_dll_directory(vlc_path)

app = QApplication(sys.argv)

window = QWidget()
layout = QVBoxLayout(window)

video_widget = QVideoWidget()
layout.addWidget(video_widget)

player = QMediaPlayer()
audio = QAudioOutput()
player.setAudioOutput(audio)
player.setVideoOutput(video_widget)

path = "input\\video1.mp4"
player = vlc.MediaPlayer(path)
player.play()

window.show()
sys.exit(app.exec())
