from typing import Any

import pytest
from pytest_mock import MockerFixture

from src.subtitles.models import Subtitles, SubtitleSegment, SubtitleWord


# --- SubtitleWord Tests ---
def test_subtitle_word_init() -> None:
    """Test initialization of SubtitleWord with trimming and correct timing."""
    word = SubtitleWord("  test  ", 1.0, 2.0)
    assert word.text == "test"
    assert word.start == 1.0
    assert word.end == 2.0


def test_subtitle_word_empty() -> None:
    """Test the empty static method of SubtitleWord returns default empty values."""
    word = SubtitleWord.empty()
    assert word.text == ""
    assert word.start == 0
    assert word.end == 0


def test_subtitle_word_equality() -> None:
    """Test equality comparison of SubtitleWord instances."""
    word1 = SubtitleWord("a", 1, 2)
    word2 = SubtitleWord("a", 1, 2)
    word3 = SubtitleWord("b", 1, 2)
    assert word1 == word2
    assert word1 != word3
    assert word1 != "not a word"


# --- SubtitleSegment Tests ---
def test_subtitle_segment_init_and_refresh() -> None:
    """Test SubtitleSegment initialization and automatic sorting/timing."""
    w1 = SubtitleWord("world", 1.0, 1.5)
    w2 = SubtitleWord("Hello", 0.5, 0.9)
    segment = SubtitleSegment([w1, w2])
    assert segment.start == 0.5
    assert segment.end == 1.5
    assert segment.words[0].text == "Hello"
    assert segment.words[1].text == "world"


def test_subtitle_segment_str() -> None:
    """Test string representation of SubtitleSegment."""
    segment = SubtitleSegment(
        [
            SubtitleWord("Hello", 0, 1),
            SubtitleWord("world.", 1, 2),
        ]
    )
    assert str(segment) == "Hello world."


def test_subtitle_segment_add_word() -> None:
    """Test adding a word to an empty SubtitleSegment."""
    segment = SubtitleSegment.empty()
    segment.add_word(SubtitleWord("New", 10.0, 11.0))
    assert len(segment.words) == 1
    assert segment.start == 10.0
    assert segment.end == 11.0


# --- Subtitles Tests ---
@pytest.fixture
def sample_transcription() -> dict[str, Any]:
    """Fixture providing a sample transcription dictionary."""
    return {
        "text": "Hello world. Test sentence.",
        "segments": [
            {
                "words": [
                    {"word": "Hello", "start": 0.1, "end": 0.5},
                    {"word": "world.", "start": 0.6, "end": 1.0},
                ]
            },
            {
                "words": [
                    {"word": "Test", "start": 2.0, "end": 2.4},
                    {"word": "sentence.", "start": 2.5, "end": 3.0},
                ]
            },
        ],
    }


def test_subtitles_from_transcription(sample_transcription: dict[str, Any], mocker: MockerFixture) -> None:
    """Test creating Subtitles from a transcription dictionary using a mocked segmenter."""
    mocker.patch(
        "src.subtitles.models.segment_words",
        return_value=[
            {"words": [{"word": "Hello", "start": 0.1, "end": 0.5}, {"word": "world.", "start": 0.6, "end": 1.0}]},
            {"words": [{"word": "Test", "start": 2.0, "end": 2.4}, {"word": "sentence.", "start": 2.5, "end": 3.0}]},
        ],
    )

    subs = Subtitles.from_transcription(sample_transcription)
    assert len(subs.segments) == 2
    assert isinstance(subs.segments[0], SubtitleSegment)
    assert len(subs.segments[0].words) == 2
    assert subs.segments[0].words[0].text == "Hello"
    assert subs.segments[0].start == 0.1
    assert subs.segments[0].end == 1.0
    assert subs.segments[1].start == 2.0
    assert subs.segments[1].end == 3.0


def test_subtitles_refresh_sorts_segments() -> None:
    """Test that Subtitles correctly sorts segments by start time."""
    seg1 = SubtitleSegment([SubtitleWord("Later", 5.0, 6.0)])
    seg2 = SubtitleSegment([SubtitleWord("First", 1.0, 2.0)])
    subs = Subtitles([seg1, seg2])
    assert subs.segments[0].start == 1.0
    assert subs.segments[1].start == 5.0


def test_subtitles_str(sample_transcription: dict[str, Any], mocker: MockerFixture) -> None:
    """Test string representation of Subtitles object."""
    mocker.patch(
        "src.subtitles.models.segment_words",
        return_value=[
            {"words": [{"word": "Hello", "start": 0.1, "end": 0.5}, {"word": "world.", "start": 0.6, "end": 1.0}]},
            {"words": [{"word": "Test", "start": 2.0, "end": 2.4}, {"word": "sentence.", "start": 2.5, "end": 3.0}]},
        ],
    )
    subs = Subtitles.from_transcription(sample_transcription)
    expected_str = "Hello world.\nTest sentence."
    assert str(subs) == expected_str
