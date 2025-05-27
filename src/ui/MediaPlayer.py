import os

from PySide6.QtGui import QCloseEvent, QShowEvent

# This PATH modification for DLLs must be effective before MPV() tries to load the DLLs.
# Setting it at the module level ensures this.
dll_directory = r"C:\Users\mw-ko\PycharmProjects\Auto-Subs\mpv-dev-x86_64-20250527-git-1d1535f"  # Replace with the actual directory
if os.path.isdir(dll_directory):
    os.environ["PATH"] = dll_directory + os.pathsep + os.environ["PATH"]
else:
    # Using print here as logger might not be configured this early.
    print(f"WARNING: MPV DLL directory not found: {dll_directory}. MPV initialization may fail.")

from mpv import MPV

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QEvent  # Slot is not directly used in this class
from logging import getLogger

logger = getLogger(__name__)


class MediaPlayer(QWidget):
    """
    A media player widget using the MPV library for video playback.
    """

    def __init__(self, parent=None):
        """
        Initialize the MediaPlayer widget. MPV instance is initialized on first show.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self.player = None  # MPV instance, initialized in _initialize_mpv
        self.mpv_initialized = False

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # It's good practice for a QWidget hosting video to have a minimum size.
        self.setMinimumSize(320, 240)

    def _initialize_mpv(self):
        """
        Initialize the MPV player instance. This should be called when the widget's window ID is valid.
        """
        if self.mpv_initialized:
            return True

        # self.winId() returns a WId (quintptr), which is compatible with HWND on Windows.
        # It needs to be cast to str for the 'wid' parameter.
        wid_val = self.winId()
        if int(wid_val) == 0:  # winId can be 0 if widget not yet created in windowing system
            logger.error("Window ID is 0. MPV cannot be initialized yet.")
            return False

        try:
            logger.debug(f"Attempting to initialize MPV with wid: {str(wid_val)}")
            self.player = MPV(
                wid=str(wid_val),
                loglevel="debug",  # As per original code
                # Common options for better integration:
                keep_open='yes',  # Keep player open when file ends
                # input_default_bindings=True, # Usually true by default
                # input_vo_keyboard=True,      # Usually true by default
                # hwdec='auto-safe' # Optional: hardware decoding
            )
            self.mpv_initialized = True
            logger.info(f"MPV player initialized successfully with wid: {str(wid_val)}.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MPV player: {e}", exc_info=True)
            self.player = None  # Ensure player is None if initialization fails
            self.mpv_initialized = False
            return False

    def showEvent(self, event: QShowEvent):
        """
        Handle widget show event to initialize MPV when wid is available.
        """
        super().showEvent(event)
        # Initialize MPV only if it hasn't been initialized yet and the widget is visible
        if not self.mpv_initialized and self.isVisible():
            if not self._initialize_mpv():
                logger.error("MPV initialization failed during showEvent. Player will not function.")
                # Consider displaying an error message on the widget itself

    def _ensure_player_ready(self):
        """Helper to check if player is initialized and ready for commands."""
        if not self.player:  # self.mpv_initialized could also be checked
            logger.warning("MPV player is not initialized or has been terminated. Operation cancelled.")
            return False
        return True

    def set_subtitles_only(self, subtitle_path: str):
        """
        Add a subtitle file for playback.
        The name "set_subtitles_only" implies exclusivity, but this implementation primarily adds the subtitle.
        MPV's default behavior or further explicit 'sid' setting would handle selection.

        Args:
            subtitle_path (str): Path to the subtitle file.
        """
        if not self._ensure_player_ready():
            return

        if not subtitle_path or not os.path.exists(subtitle_path):
            logger.warning(f"Invalid or non-existent subtitle path: {subtitle_path}. Cannot set subtitles.")
            return

        logger.info(f"Adding subtitles: {subtitle_path}")
        try:
            # Check if media is loaded. Adding subs without media might be valid for mpv,
            # but they won't display. Contextually, subs are usually for current video.
            if not self.player.filename:
                logger.warning("No media loaded. Subtitles will be added but may not display until media plays.")

            self.player.sub_add(subtitle_path)
            self.player.sub_visibility = True  # Ensure subtitles are globally enabled

            # mpv often auto-selects newly added external subtitles.
            # If explicit selection of *only* this sub is required, one would need to:
            # 1. Find the ID of the newly added track (e.g., from self.player.track_list).
            # 2. Set self.player.sid = new_track_id.
            # This is omitted for simplicity, relying on mpv's auto-selection.

            self.player.sub_reload()  # Reloads all assigned subtitle files
            logger.info(f"Subtitles added and reloaded: {subtitle_path}")
        except Exception as e:
            logger.error(f"Failed to set subtitles: {e}", exc_info=True)

    def set_media(self, video_path: str, subtitle_path: str = None):
        """
        Set the media file and optional subtitle file for playback.

        Args:
            video_path (str): Path to the video file.
            subtitle_path (str, optional): Path to the subtitle file. Defaults to None.
        """
        if not self._ensure_player_ready():
            return

        if not video_path or not os.path.exists(video_path):
            logger.warning(f"Invalid or non-existent video path: {video_path}. Cannot set media.")
            return

        logger.info(f"Setting media: {video_path}, subtitles: {subtitle_path}")
        try:
            # self.player.stop() # Not strictly needed as loadfile (default mode 'replace') stops current playback.
            self.player.loadfile(video_path)  # Default mode is 'replace'

            if subtitle_path:
                # Call set_subtitles_only AFTER video is loaded.
                # The check for subtitle_path existence is now inside set_subtitles_only.
                self.set_subtitles_only(subtitle_path)
            # If no subtitle_path, mpv handles default subtitle selection (e.g., embedded).
        except Exception as e:
            logger.error(f"Failed to set media: {e}", exc_info=True)

    def play(self):  # Method name kept as per user requirement
        """Play the media by unpausing."""
        if not self._ensure_player_ready():
            return

        try:
            if not self.player.filename:  # Check if a file is loaded
                logger.warning("No media loaded. Cannot play.")
                return
            self.player.pause = False  # Correct way to unpause/play
            logger.info("Playback started (unpaused).")
        except Exception as e:
            logger.error(f"Failed to play/unpause media: {e}", exc_info=True)

    def pause(self):
        """Pause media playback."""
        if not self._ensure_player_ready():
            return

        try:
            if not self.player.filename:
                logger.warning("No media loaded. Cannot pause.")
                return

            # Optional: Check if already paused
            # if self.player.pause:
            #     logger.info("Playback is already paused.")
            #     return

            self.player.pause = True
            logger.info("Playback paused.")
        except Exception as e:
            logger.error(f"Failed to pause media: {e}", exc_info=True)

    def set_timestamp(self, timestamp: int):
        """
        Set the playback position to the given timestamp.

        Args:
            timestamp (int): The timestamp in milliseconds.
        """
        if not self._ensure_player_ready():
            return

        try:
            if not self.player.filename:
                logger.warning("No media loaded. Cannot set timestamp.")
                return

            seconds = timestamp / 1000.0
            self.player.time_pos = seconds
            logger.info(f"Playback position set to {seconds:.3f}s ({timestamp}ms).")
        except Exception as e:
            logger.error(f"Failed to set timestamp: {e}", exc_info=True)

    def closeEvent(self, event: QCloseEvent):
        """
        Handle widget close event to release MPV resources.

        Args:
            event: The close event.
        """
        logger.info("MediaPlayer closeEvent triggered.")
        if self.player:  # Check if player instance exists and hasn't been terminated
            try:
                logger.info("Terminating MPV player...")
                self.player.terminate()
                logger.info("MPV player terminated successfully.")
            except Exception as e:
                logger.error(f"Error during MPV termination: {e}", exc_info=True)
            finally:
                self.player = None  # Clear the reference
                self.mpv_initialized = False  # Reset the flag
        super().closeEvent(event)
