# src/managers/transcription_manager.py
import asyncio
import threading
from logging import getLogger
from pathlib import Path
from typing import Any, cast

import whisper

from src.config import WHISPER_MODEL
from src.managers.base_manager import BaseManager, EventType

logger = getLogger(__name__)


TranscriptionResult = dict[str, str | list[dict[str, int]]]


class TranscriptionEventType(EventType):
    """Defines the event types for the TranscriptionManager."""

    TRANSCRIPTION_CHANGED = "on_transcription_changed"
    TRANSCRIPTION_FAILED = "on_transcription_failed"
    TRANSCRIPTION_CANCELLED = "on_transcription_cancelled"


class TranscriptionManager(BaseManager[Any]):
    """
    Manages asynchronous transcription using OpenAI's Whisper model.

    This class loads the Whisper model in a background thread and provides
    an asynchronous interface to transcribe audio files. It also supports
    listener registration to notify external components when transcription completes.
    """

    def __init__(self, whisper_model: str = WHISPER_MODEL) -> None:
        """
        Initialize the TranscriptionManager and begin loading the Whisper model.

        Args:
            whisper_model (str): Name or path of the Whisper model to load.
        """
        super().__init__(TranscriptionEventType)
        self._model: whisper.Whisper | None = None
        self._model_lock = asyncio.Lock()

        self._model_loaded_event = threading.Event()
        self._model_loading_thread: threading.Thread | None = None
        self._current_audio_path: Path | None = None
        self._is_cancellation_requested = False

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
    ) -> TranscriptionResult | None:
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
                result = cast(
                    TranscriptionResult,
                    await asyncio.to_thread(
                        self._model.transcribe,
                        audio=str(audio_path),
                        word_timestamps=word_timestamps,
                        language=language,
                    ),
                )
                if self._is_cancellation_requested:
                    logger.info("Transcription was cancelled. Discarding result.")
                    self._notify_listeners({}, TranscriptionEventType.TRANSCRIPTION_CANCELLED)
                    return None

                if self._current_audio_path != audio_path:
                    logger.debug("Transcription result discarded due to source change.")
                    return None

                logger.info("Transcription completed successfully.")
                self._notify_listeners(result, TranscriptionEventType.TRANSCRIPTION_CHANGED)
                return result

            except Exception as e:
                logger.exception("Error during transcription")
                self._notify_listeners(e, TranscriptionEventType.TRANSCRIPTION_FAILED)
                return None

    def on_video_changed(self, video_path: Path) -> None:
        """
        Update the manager with the current video path.

        This is called when a new video is loaded to keep the manager's state
        in sync and prevent stale transcription results from being applied.

        Args:
            video_path: The path to the newly loaded video.
        """
        self._current_audio_path = video_path

    def start_transcription(self) -> None:
        """
        Start the transcription process for the video path currently held by the manager.

        This is intended to be called manually (e.g., by a button press).
        """
        if not self._current_audio_path:
            logger.warning("Transcription started with no video path set.")
            return

        self._is_cancellation_requested = False
        audio_path_to_transcribe = self._current_audio_path
        logger.info(f"Manual transcription initiated for: {audio_path_to_transcribe}")
        asyncio.create_task(self.transcribe(audio_path_to_transcribe))

    def cancel_transcription(self) -> None:
        """Request cancellation of the ongoing transcription task."""
        self._is_cancellation_requested = True
        logger.info("Transcription cancellation requested.")
