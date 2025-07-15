import asyncio
import threading
from logging import getLogger
from pathlib import Path
from typing import Any, Callable

import whisper

from src.utils.constants import WHISPER_MODEL

logger = getLogger(__name__)


class TranscriptionManager:
    """
    Manages asynchronous transcription using OpenAI's Whisper model.

    This class loads the Whisper model in a background thread and provides
    an asynchronous interface to transcribe audio files. It also supports
    listener registration to notify external components when transcription completes.
    """

    def __init__(self, whisper_model: str = WHISPER_MODEL):
        """
        Initialize the TranscriptionManager and begin loading the Whisper model.

        Args:
            whisper_model (str): Name or path of the Whisper model to load.
        """
        self._model = None
        self._model_lock = asyncio.Lock()
        self._transcription_listeners: list[Callable[[dict[str, Any]], None]] = []
        self._model_loaded_event = threading.Event()
        self._model_loading_thread: threading.Thread | None = None
        self._current_audio_path: Path | None = None

        self._load_model(whisper_model)

    def _load_model(self, whisper_model: str) -> None:
        """
        Load the Whisper model in a separate thread to avoid blocking the main thread.

        Args:
            whisper_model (str): The model name (e.g., 'base', 'small') or file path.
        """

        def worker() -> None:
            try:
                logger.info("Loading Whisper model...")
                self._model = whisper.load_model(whisper_model)
                logger.info("Whisper model loaded successfully.")
            except Exception as e:
                logger.exception("Failed to load Whisper model")
                raise RuntimeError(f"Model loading failed: {e}") from e
            finally:
                self._model_loaded_event.set()

        self._model_loading_thread = threading.Thread(target=worker, daemon=True)
        self._model_loading_thread.start()

    async def transcribe(
        self, audio_path: Path, word_timestamps: bool = True, language: str | None = None
    ) -> dict[str, Any] | None:
        """
        Asynchronously transcribe an audio file using the loaded Whisper model.

        Args:
            audio_path (str): Path to the input audio file.
            word_timestamps (bool): Whether to include word-level timestamps.
            language (Optional[str]): Optional language code to assist transcription.

        Returns:
            dict | None: Transcription result dictionary if successful, else None.
        """
        await asyncio.to_thread(self._model_loaded_event.wait)

        if self._model is None:
            raise RuntimeError("Whisper model failed to load or is unavailable.")

        async with self._model_lock:
            if self._current_audio_path != audio_path:
                logger.debug(f"Ignoring outdated transcription request for: {audio_path}")
                return None

            try:
                logger.info(f"Starting transcription for: {audio_path}")
                result = await asyncio.to_thread(
                    self._model.transcribe,
                    audio=str(audio_path),
                    word_timestamps=word_timestamps,
                    language=language,
                )
                if self._current_audio_path != audio_path:
                    logger.debug("Transcription result discarded due to source change.")
                    return None

                logger.info("Transcription completed successfully.")
                self._notify_listeners(result)
                return result

            except Exception as e:
                logger.exception("Error during transcription")
                raise RuntimeError(f"Transcription failed: {e}") from e

    def add_transcription_listener(self, listener: Callable[[dict[str, Any]], None]) -> None:
        """
        Register a listener to be called when transcription completes.

        Args:
            listener (Callable[[dict], None]): A callback function that takes
                the transcription result as an argument.
        """
        self._transcription_listeners.append(listener)

    def _notify_listeners(self, transcription: dict[str, Any]) -> None:
        """
        Notify all registered listeners with the transcription result.

        Args:
            transcription (dict): The completed transcription result.
        """
        for listener in self._transcription_listeners:
            try:
                listener(transcription)
            except Exception as e:
                logger.warning(f"Listener raised an exception: {e}")

    def on_video_changed(self, video_path: Path) -> None:
        """
        Trigger transcription for a new video or audio source.

        Args:
            video_path (str): Path to the new video/audio file.
        """
        self._current_audio_path = video_path
        asyncio.create_task(self.transcribe(video_path))
