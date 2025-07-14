from typing import Any

import pytest

from src.subtitles.segmenter import segment_words


@pytest.fixture
def transcription_data() -> dict[str, Any]:
    """Return a sample transcription with a sequence of words and timestamps."""
    return {
        "segments": [
            {
                "words": [
                    {"word": "This", "start": 0.0, "end": 0.2},
                    {"word": "is", "start": 0.2, "end": 0.4},
                    {"word": "a", "start": 0.4, "end": 0.5},
                    {"word": "test,", "start": 0.5, "end": 0.8},
                    {"word": "another", "start": 1.0, "end": 1.4},
                    {"word": "one", "start": 1.5, "end": 1.7},
                    {"word": "follows.", "start": 1.8, "end": 2.2},
                ]
            }
        ]
    }


def test_segment_by_max_chars(transcription_data: dict[str, Any]) -> None:
    """Segment words based on a character length limit."""
    segments = segment_words(transcription_data, max_chars=20)
    assert len(segments) == 2
    assert segments[0]["text"] == "This is a test,"
    assert segments[0]["start"] == 0.0
    assert segments[0]["end"] == 0.8
    assert segments[1]["text"] == "another one follows."
    assert segments[1]["start"] == 1.0
    assert segments[1]["end"] == 2.2


def test_segment_by_break_chars(transcription_data: dict[str, Any]) -> None:
    """Segment words based on specified punctuation characters."""
    segments = segment_words(transcription_data, max_chars=100, break_chars=(",",))
    assert len(segments) == 2
    assert segments[0]["text"] == "This is a test,"
    assert segments[1]["text"] == "another one follows."


def test_remaining_buffer_is_added(transcription_data: dict[str, Any]) -> None:
    """Ensure leftover words are added to a final segment if no break char is found."""
    segments = segment_words(transcription_data, max_chars=100, break_chars=("?",))
    assert len(segments) == 1
    assert segments[0]["text"] == "This is a test, another one follows."
    assert segments[0]["start"] == 0.0
    assert segments[0]["end"] == 2.2


def test_empty_transcription() -> None:
    """Return no segments when input contains no word data."""
    segments = segment_words({"segments": []})
    assert len(segments) == 0


def test_invalid_transcription_format() -> None:
    """Raise an error when transcription input is missing the 'segments' key."""
    with pytest.raises(ValueError, match="Invalid transcription format: missing key 'segments'"):
        segment_words({})
