from logging import getLogger
from typing import Any, Union

logger = getLogger(__name__)


def segment_words(
    transcription: dict[str, list[dict[str, Any]]],
    max_chars: int = 10,
    break_chars: tuple[str, ...] = (".", ",", "!", "?"),
) -> list[dict[str, Any]]:
    """
    Segments a transcription into subtitle chunks based on character limits
    and punctuation.

    Args:
        transcription (dict): A dictionary containing segments with word-level data.
        max_chars (int): The maximum number of characters per subtitle line.
        break_chars (tuple): Characters that signal where to break the line (e.g., punctuation marks).

    Returns:
        list: A list of dictionaries representing subtitle segments.
    """
    words = []
    try:
        for segment in transcription["segments"]:
            segmented_words = segment.get("words", [])
            # filtrujemy tylko słowniki (unika problemów z nieoczekiwanymi typami)
            filtered_words = [w for w in segmented_words if isinstance(w, dict)]
            words.extend(filtered_words)
    except KeyError as e:
        logger.error(f"Invalid transcription format: missing key {e}")
        raise ValueError(f"Invalid transcription format: missing key {e}") from e

    segments = []
    buffer: list[dict[str, Any]] = []
    segment_start: Union[float, None] = None

    for word in words:
        # Sprawdzamy, czy word jest dict (na wszelki wypadek)
        if not isinstance(word, dict):
            continue

        raw_word = word.get("word", "")
        if not isinstance(raw_word, str):
            continue

        word_text = raw_word.strip()
        if not word_text:
            continue

        if not buffer:
            start_val = word.get("start")
            segment_start = float(start_val) if isinstance(start_val, (int, float)) else None

        buffer.append(word)
        combined_text = " ".join(
            w.get("word", "").strip() if isinstance(w.get("word", ""), str) else "" for w in buffer
        )

        is_long = len(combined_text) >= max_chars
        is_break_char = word_text[-1] in break_chars if word_text else False

        if is_long or is_break_char:
            if segment_start is not None:
                end_val = word.get("end")
                segments.append(
                    {
                        "start": segment_start,
                        "end": float(end_val) if isinstance(end_val, (int, float)) else 0.0,
                        "text": combined_text.strip(),
                        "words": buffer.copy(),
                    }
                )
            buffer.clear()
            segment_start = None

    if buffer and segment_start is not None:
        end_val = buffer[-1].get("end")
        segments.append(
            {
                "start": segment_start,
                "end": float(end_val) if isinstance(end_val, (int, float)) else 0.0,
                "text": " ".join(
                    w.get("word", "").strip() if isinstance(w.get("word", ""), str) else "" for w in buffer
                ),
                "words": buffer.copy(),
            }
        )

    logger.info(f"Segmentation complete: {len(segments)} subtitle chunks created.")
    return segments
