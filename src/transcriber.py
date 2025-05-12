import threading
import whisper
import logging
from src.utils.constants import WHISPER_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Whisper model and define a thread lock
_model = whisper.load_model(WHISPER_MODEL)
_model_lock = threading.Lock()


def transcribe(audio_path: str, word_timestamps: bool = True) -> dict[str, any]:
    """
    Transcribes an audio file to text using the Whisper model.

    Args:
        audio_path (str): Path to the input audio file.
        word_timestamps (bool): Whether to include word-level timestamps.

    Returns:
        dict: Transcription result from the Whisper model.

    Raises:
        RuntimeError: If transcription fails.
    """
    with _model_lock:
        try:
            return _model.transcribe(audio_path, word_timestamps=word_timestamps)
        except Exception as e:
            logger.exception("Transcription failed")
            raise RuntimeError(f"Transcription failed: {e}") from e
