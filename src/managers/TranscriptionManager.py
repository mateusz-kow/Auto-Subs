import asyncio
import threading
import whisper
import logging
from src.utils.constants import WHISPER_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptionManager:
    def __init__(self, whisper_model: str = WHISPER_MODEL):
        self.model = None
        self.model_loading_thread = None
        self.transcription_listeners = []
        self.model_loaded_event = threading.Event()  # Event to signal model loading completion
        self.load_model(whisper_model)

    def load_model(self, whisper_model: str):
        """
        Loads the Whisper model in a separate thread.
        """

        def worker():
            try:
                logger.info("Loading Whisper model...")
                self.model = whisper.load_model(whisper_model)
                logger.info("Whisper model loaded successfully.")
                self.model_loaded_event.set()  # Signal that the model is loaded
            except Exception as e:
                logger.exception("Failed to load Whisper model")
                self.model_loaded_event.set()  # Ensure the event is set even on failure
                raise RuntimeError(f"Failed to load model: {e}") from e

        # Start the worker in a separate thread
        self.model_loading_thread = threading.Thread(target=worker, daemon=True)
        self.model_loading_thread.start()

    async def transcribe(self, audio_path: str, word_timestamps: bool = True):
        """
        Asynchronously transcribes an audio file to text using the Whisper model.

        Args:
            audio_path (str): Path to the input audio file.
            word_timestamps (bool): Whether to include word-level timestamps.

        Returns:
            dict: Transcription result.
        """
        # Wait for the model to load
        await asyncio.to_thread(self.model_loaded_event.wait)

        if not self.model:
            raise RuntimeError("Model is not loaded. Cannot transcribe.")

        try:
            logger.info(f"Starting transcription for {audio_path}...")
            transcription = await asyncio.to_thread(
                self.model.transcribe, audio_path, word_timestamps=word_timestamps
            )
            logger.info("Transcription completed successfully.")
            await self.notify_listeners(transcription)
            return transcription
        except Exception as e:
            logger.exception("Transcription failed")
            raise RuntimeError(f"Transcription failed: {e}") from e

    async def notify_listeners(self, transcription):
        """
        Notifies all listeners with the transcription result.

        Args:
            transcription (dict): Transcription result from the Whisper model.
        """
        for listener in self.transcription_listeners:
            await listener(transcription)

    def add_transcription_listener(self, listener):
        """
        Adds a listener to be notified when transcription is complete.

        Args:
            listener (callable): A coroutine function to call with the transcription result.
        """
        self.transcription_listeners.append(listener)

    def on_video_changed(self, video_path: str):
        """
        Called when the video changes. Can be used to reset or update the transcription manager.

        Args:
            video_path (str): Path to the new video file.
        """
        asyncio.create_task(self.transcribe(video_path))