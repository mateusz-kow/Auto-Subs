# Constants for customization
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

BAR_HEIGHT = 25
SUBTITLE_BAR_HEIGHT = 20
VIDEO_BAR_Y = 40  # Adjusted to leave space for markers
SUBTITLE_BAR_Y = 70
SCENE_MIN_WIDTH = 1000
TIME_SCALE_FACTOR = 50  # Adjust scaling for width
VIDEO_BAR_COLOR = QColor(100, 150, 200)  # Blue
SUBTITLE_BAR_COLOR = QColor(200, 100, 100)  # Red
MARKER_INTERVAL = 5  # Interval for markers in seconds
MARKER_Y = 5  # Y position for markers
MARKER_LINE_HEIGHT = 15  # Height of marker lines
MARKER_TEXT_OFFSET = 20  # Offset for marker text
MAJOR_MARKER_INTERVAL = 5
MINOR_MARKER_INTERVAL = 1
MAJOR_MARKER_HEIGHT = 5
MINOR_MARKER_HEIGHT = 2
MARKER_COLOR = Qt.GlobalColor.black
SPECIAL_MARKER_COLOR = Qt.GlobalColor.red  # For special markers
FRAME_RATE = 60
SELECTED_SEGMENT_COLOR = Qt.GlobalColor.green
