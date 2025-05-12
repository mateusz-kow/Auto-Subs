import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def segment_words(
        transcription: Dict[str, List[Dict[str, float]]],
        max_chars: int = 10,
        break_chars: tuple = ('.', ',', '!', '?')
) -> List[Dict[str, any]]:
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
            for word in segment.get("words", []):
                words.append(word)
    except KeyError as e:
        logger.error(f"Invalid transcription format: missing key {e}")
        raise ValueError(f"Invalid transcription format: missing key {e}")

    segments = []
    buffer = []
    segment_start = None

    for word in words:
        word_text = word["word"].strip()
        if not word_text:
            continue

        if not buffer:
            segment_start = word["start"]

        buffer.append(word)
        combined_text = " ".join(w["word"].strip() for w in buffer)

        is_long = len(combined_text) >= max_chars
        is_break_char = word_text[-1] in break_chars

        if is_long or is_break_char:
            segments.append({
                "start": segment_start,
                "end": word["end"],
                "text": combined_text.strip(),
                "words": buffer.copy()
            })
            buffer.clear()
            segment_start = None

    if buffer and segment_start is not None:
        segments.append({
            "start": segment_start,
            "end": buffer[-1]["end"],
            "text": " ".join(w["word"].strip() for w in buffer),
            "words": buffer.copy()
        })

    logger.info(f"Segmentation complete: {len(segments)} subtitle chunks created.")
    return segments
