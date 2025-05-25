import logging
import vlc
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Slot, QCoreApplication
from src.utils.logger_config import get_logger
logger = get_logger(__name__)


class MediaPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create VLC instance and media player
        # Te obiekty powinny być tworzone raz na żywotność widgetu
        self.instance = vlc.Instance()
        if not self.instance:
            logger.error("Failed to create VLC instance.")
            # Handle error appropriately, e.g., raise exception or disable functionality
            return
        self.media_player = self.instance.media_player_new()
        if not self.media_player:
            logger.error("Failed to create VLC media player.")
            # Handle error
            return

        # Get event manager
        self.event_manager = self.media_player.event_manager()

        # Flag to ensure preview setup runs only once per media
        self._preview_setup_pending = False
        self._is_shutting_down = False  # Flag to prevent operations during shutdown

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # HWND will be set in showEvent for reliability

    def showEvent(self, event):
        """Called when the widget is shown."""
        super().showEvent(event)
        # This is the most reliable place to set HWND for the first time
        # as winId() is guaranteed to be valid.
        if self.winId() and self.media_player:
            logger.info(f"MediaPlayer widget shown. Setting HWND to {self.winId()}")
            self.media_player.set_hwnd(self.winId())
        else:
            logger.warning("Could not set HWND in showEvent: winId() or media_player not ready.")

    def set_media(self, video_path: str, subtitle_path: str = None):
        """
        Set the media file and optional subtitle file.
        This method handles the necessary changes when a new video is loaded.
        """
        if self._is_shutting_down or not self.media_player:
            logger.warning("set_media called during shutdown or media_player not initialized.")
            return

        logger.info(f"Setting media: {video_path}, subtitles: {subtitle_path}")

        # 1. Stop any current playback and clear state related to old media
        if self.media_player.is_playing() or self.media_player.get_state() == vlc.State.Paused:
            self.media_player.stop()
            # Give VLC a moment to process the stop command, especially if changing media rapidly
            QCoreApplication.processEvents()

        self._preview_setup_pending = False  # Cancel any pending preview from previous media

        # 2. Detach previous event listeners to avoid multiple triggers or calls on old media
        try:
            # Check if event_manager is still valid (it should be unless release_player was called)
            if self.event_manager and hasattr(self.event_manager, 'event_detach'):
                self.event_manager.event_detach(vlc.EventType.MediaPlayerPlaying)
                self.event_manager.event_detach(vlc.EventType.MediaPlayerEncounteredError)
        except Exception as e:
            logger.debug(f"Error detaching previous event listeners: {e} (might be first run or already detached)")

        # 3. Create new media object
        if subtitle_path:
            media = self.instance.media_new(video_path, f":sub-file={subtitle_path}")
        else:
            media = self.instance.media_new(video_path)

        if not media:
            logger.error(f"Failed to create media for: {video_path}")
            return

        # 4. Set the new media to the player
        self.media_player.set_media(media)
        media.release()  # Release media object as VLC holds a reference

        # 5. Ensure HWND is set. Usually set in showEvent, but if set_media
        #    is called after widget is created but before shown, winId might be 0.
        #    If widget is already shown, winId() is valid.
        #    Re-setting it here might be redundant but generally harmless.
        #    If showEvent hasn't run yet, this might log a warning.
        if self.winId():
            self.media_player.set_hwnd(self.winId())
        else:
            logger.warning(
                "winId is not available yet during set_media. Video output might not be set until widget is shown.")

        # 6. Attach event listeners for the new media
        # Ensure event_manager is valid before attaching
        if self.event_manager and hasattr(self.event_manager, 'event_attach'):
            self.event_manager.event_attach(
                vlc.EventType.MediaPlayerPlaying, self._on_media_player_playing
            )
            self.event_manager.event_attach(
                vlc.EventType.MediaPlayerEncounteredError, self._on_media_player_error
            )
        else:
            logger.error("Cannot attach VLC events, event_manager is not available.")
            return

        # 7. Initiate playback to fetch the first frame for preview
        self._preview_setup_pending = True
        self.media_player.play()
        logger.info("Media playback initiated for preview. Waiting for 'Playing' event.")

    @Slot(vlc.Event)
    def _on_media_player_playing(self, event):
        if self._is_shutting_down: return
        logger.debug(f"VLC Event: MediaPlayerPlaying (preview_pending: {self._preview_setup_pending})")
        if self._preview_setup_pending:
            # Schedule UI-related part on the main Qt thread
            QTimer.singleShot(0, self._setup_preview_frame)

    @Slot(vlc.Event)
    def _on_media_player_error(self, event):
        if self._is_shutting_down: return
        logger.error("VLC Event: MediaPlayerEncounteredError. Media playback failed.")
        self._preview_setup_pending = False
        try:
            if self.event_manager and hasattr(self.event_manager, 'event_detach'):
                self.event_manager.event_detach(vlc.EventType.MediaPlayerPlaying)
        except Exception as e:
            logger.debug(f"Error detaching MediaPlayerPlaying on error: {e}")

    @Slot()
    def _setup_preview_frame(self):
        """This method is called on the main Qt thread to finalize preview."""
        if self._is_shutting_down or not self.media_player: return
        if not self._preview_setup_pending:
            logger.debug("Preview setup was cancelled or already done.")
            return

        logger.info("Setting up preview frame (pause and next_frame).")
        current_state = self.media_player.get_state()
        logger.debug(f"Current media player state for preview: {current_state}")

        if current_state == vlc.State.Playing:
            self.media_player.pause()
            # Give a tiny moment for pause to take effect before seeking
            # QTimer.singleShot(10, self._seek_to_first_frame_for_preview) # Alternative
            self._seek_to_first_frame_for_preview()

        else:
            logger.warning(f"Cannot setup preview frame. Player not in 'Playing' state. Current state: {current_state}")
            self._preview_setup_pending = False  # Failed, so reset flag

        # Detach the one-shot event listener after it has served its purpose for THIS preview
        try:
            if self.event_manager and hasattr(self.event_manager, 'event_detach'):
                self.event_manager.event_detach(vlc.EventType.MediaPlayerPlaying)
        except Exception as e:
            logger.debug(f"Error detaching MediaPlayerPlaying after preview attempt: {e}")

    @Slot()  # Helper for _setup_preview_frame to ensure pause takes effect
    def _seek_to_first_frame_for_preview(self):
        if self._is_shutting_down or not self.media_player: return

        # Using set_position(0.0) or set_time(0) or set_time(1) can be more reliable for the very first frame
        self.media_player.set_position(0.0)  # Seek to beginning
        # Some versions/platforms might need a nudge with next_frame or a small delay
        # success = self.media_player.next_frame()
        # if not success:
        #    logger.warning("next_frame() failed or not supported for preview. Relaying on set_position(0).")

        # Ensure it's paused after seek, as seek might resume on some platforms
        # Wait a brief moment for the seek and then ensure pause
        QTimer.singleShot(50, self._finalize_preview_pause)

    @Slot()
    def _finalize_preview_pause(self):
        if self._is_shutting_down or not self.media_player: return

        if self.media_player.is_playing():
            self.media_player.pause()
        logger.info("Updated video preview (media set to first frame and paused).")
        self._preview_setup_pending = False  # Preview setup is done

    def play(self):
        """Play the media."""
        if self._is_shutting_down or not self.media_player: return
        if not self.media_player.get_media():
            logger.warning("No media set. Cannot play.")
            return
        logger.debug("MediaPlayer: Play called.")
        self._preview_setup_pending = False  # User explicitly called play, cancel any preview setup
        self.media_player.play()

    def pause(self):
        """Pause the media."""
        if self._is_shutting_down or not self.media_player: return
        if not self.media_player.get_media():
            logger.warning("No media set. Cannot pause.")
            return
        logger.debug("MediaPlayer: Pause called.")
        self.media_player.pause()

    def set_timestamp(self, timestamp: int):
        """Set the playback position to the given timestamp (in milliseconds)."""
        if self._is_shutting_down or not self.media_player: return
        if not self.media_player.get_media():
            logger.warning("No media set. Cannot set timestamp.")
            return
        logger.debug(f"MediaPlayer: Setting timestamp to {timestamp}ms.")
        self._preview_setup_pending = False  # If seeking, we are past preview stage
        self.media_player.set_time(timestamp)

    def release_player(self):
        """Release VLC player resources."""
        logger.info("Releasing media player resources.")
        self._is_shutting_down = True  # Signal that we are shutting down

        if self.media_player:
            # Detach all events before stopping and releasing
            # Check if event_manager exists and has the method (could be None if init failed or already released)
            if self.event_manager and hasattr(self.event_manager, 'event_detach'):
                try:
                    self.event_manager.event_detach(vlc.EventType.MediaPlayerPlaying)
                    self.event_manager.event_detach(vlc.EventType.MediaPlayerEncounteredError)
                    # Detach any other events you might have attached
                except Exception as e:
                    logger.debug(f"Error detaching events during release: {e}")

            if self.media_player.is_playing():
                self.media_player.stop()

            current_media = self.media_player.get_media()
            if current_media:
                current_media.release()  # Release the media object if any
                self.media_player.set_media(None)  # Detach media from player

            self.media_player.release()
            self.media_player = None
            self.event_manager = None  # Clear event manager as it's tied to media_player

        if self.instance:
            self.instance.release()
            self.instance = None
        logger.info("Media player resources released.")

    def closeEvent(self, event):
        """Handle widget close event to release VLC resources."""
        logger.debug("MediaPlayer closeEvent triggered.")
        self.release_player()
        super().closeEvent(event)