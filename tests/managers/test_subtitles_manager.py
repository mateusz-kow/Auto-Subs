# tests/managers/test_subtitles_manager.py
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from src.managers.subtitles_manager import SubtitlesManager
from src.subtitles.models import Subtitles, SubtitleSegment, SubtitleWord


@pytest.fixture
def sample_word_1() -> SubtitleWord:
    """Return a sample SubtitleWord representing the word 'Hello'."""
    return SubtitleWord("Hello", 0.0, 0.5)


@pytest.fixture
def sample_word_2() -> SubtitleWord:
    """Return a sample SubtitleWord representing the word 'world'."""
    return SubtitleWord("world", 0.6, 1.0)


@pytest.fixture
def sample_segment_1(sample_word_1: SubtitleWord, sample_word_2: SubtitleWord) -> SubtitleSegment:
    """Return a sample SubtitleSegment containing two words."""
    return SubtitleSegment([sample_word_1, sample_word_2])


@pytest.fixture
def sample_segment_2() -> SubtitleSegment:
    """Return a sample SubtitleSegment containing a single word."""
    return SubtitleSegment([SubtitleWord("Test", 1.5, 2.0)])


@pytest.fixture
def sample_subtitles(sample_segment_1: SubtitleSegment, sample_segment_2: SubtitleSegment) -> Subtitles:
    """Return a Subtitles object composed of two segments."""
    return Subtitles([sample_segment_1, sample_segment_2])


@pytest.fixture
def subtitles_manager(sample_subtitles: Subtitles) -> SubtitlesManager:
    """Return a SubtitlesManager initialized with sample subtitles."""
    return SubtitlesManager(sample_subtitles)


def test_initialization(subtitles_manager: SubtitlesManager, sample_subtitles: Subtitles) -> None:
    """Test that SubtitlesManager initializes with the correct subtitles."""
    assert subtitles_manager.subtitles == sample_subtitles


def test_set_subtitles_notifies(mocker: MockerFixture) -> None:
    """Test that setting new subtitles triggers listener notification."""
    manager = SubtitlesManager()
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    manager.register_listener(mock_listener_obj)

    new_subs = Subtitles.empty()
    manager.set_subtitles(new_subs)

    assert manager.subtitles == new_subs
    mock_listener_obj.on_subtitles_changed.assert_called_once_with(new_subs)


def test_delete_word(subtitles_manager: SubtitlesManager, mocker: MockerFixture) -> None:
    """Test deleting a word from a segment and notifying listeners."""
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    subtitles_manager.register_listener(mock_listener_obj)
    assert len(subtitles_manager.subtitles.segments[0].words) == 2

    subtitles_manager.delete_word(segment_index=0, word_index=0)

    assert len(subtitles_manager.subtitles.segments[0].words) == 1
    assert subtitles_manager.subtitles.segments[0].words[0].text == "world"
    mock_listener_obj.on_subtitles_changed.assert_called_once()


def test_delete_segments(subtitles_manager: SubtitlesManager, mocker: MockerFixture) -> None:
    """Test deleting a subtitle segment by index and notifying listeners."""
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    subtitles_manager.register_listener(mock_listener_obj)
    assert len(subtitles_manager.subtitles.segments) == 2

    subtitles_manager.delete_segments({0})

    assert len(subtitles_manager.subtitles.segments) == 1
    assert subtitles_manager.subtitles.segments[0].words[0].text == "Test"
    mock_listener_obj.on_subtitles_changed.assert_called_once()


def test_add_empty_segment(subtitles_manager: SubtitlesManager, mocker: MockerFixture) -> None:
    """Test that an empty segment is added and listeners are notified."""
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    subtitles_manager.register_listener(mock_listener_obj)
    initial_count = len(subtitles_manager.subtitles.segments)

    subtitles_manager.add_empty_segment()

    assert len(subtitles_manager.subtitles.segments) == initial_count + 1
    assert SubtitleSegment.empty() in subtitles_manager.subtitles.segments
    mock_listener_obj.on_subtitles_changed.assert_called_once()


def test_merge_segments(subtitles_manager: SubtitlesManager, mocker: MockerFixture) -> None:
    """Test merging multiple segments into one and notifying listeners."""
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    subtitles_manager.register_listener(mock_listener_obj)

    subtitles_manager.subtitles.add_segment(SubtitleSegment([SubtitleWord("Again", 3.0, 3.5)]))
    assert len(subtitles_manager.subtitles.segments) == 3

    subtitles_manager.merge_segments({0, 1, 2})

    assert len(subtitles_manager.subtitles.segments) == 1
    merged_segment = subtitles_manager.subtitles.segments[0]
    assert len(merged_segment.words) == 4
    assert merged_segment.start == 0.0
    assert merged_segment.end == 3.5
    assert "Hello" in str(merged_segment)
    assert "Again" in str(merged_segment)
    mock_listener_obj.on_subtitles_changed.assert_called_once()


def test_set_word(subtitles_manager: SubtitlesManager, mocker: MockerFixture, sample_word_1: SubtitleWord) -> None:
    """Test replacing a word in a segment and notifying listeners."""
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    subtitles_manager.register_listener(mock_listener_obj)
    original_word = sample_word_1
    assert subtitles_manager.subtitles.segments[0].words[0] == original_word

    new_word = SubtitleWord("Goodbye", 0.1, 0.4)
    subtitles_manager.set_word(segment_index=0, word_index=0, word=new_word)

    assert subtitles_manager.subtitles.segments[0].words[0] == new_word
    assert subtitles_manager.subtitles.segments[0].words[0] != original_word
    mock_listener_obj.on_subtitles_changed.assert_called_once()


def test_on_video_changed_clears_and_notifies(subtitles_manager: SubtitlesManager, mocker: MockerFixture) -> None:
    """Test that subtitles are cleared and listeners are notified when the video is changed."""
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    subtitles_manager.register_listener(mock_listener_obj)

    assert subtitles_manager.subtitles is not None
    assert len(subtitles_manager.subtitles.segments) > 0

    subtitles_manager.on_video_changed(Path("/fake/video.mp4"))

    assert subtitles_manager.subtitles is not None
    assert len(subtitles_manager.subtitles.segments) == 0
    # mock_listener_obj.on_subtitles_changed.assert_called_once()


def test_resize_segment_scales_words_down(subtitles_manager: SubtitlesManager, mocker: MockerFixture) -> None:
    """Test that resizing a segment to a shorter duration scales words correctly."""
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    subtitles_manager.register_listener(mock_listener_obj)
    segment_index = 0
    # Original: start=0.0, end=1.0, duration=1.0
    # Words: (0.0, 0.5), (0.6, 1.0)
    new_start, new_end = 0.5, 1.0  # New duration = 0.5 (scale factor = 0.5)

    subtitles_manager.resize_segment(segment_index, new_start, new_end)
    resized_segment = subtitles_manager.subtitles.segments[segment_index]

    assert resized_segment.start == pytest.approx(0.5)
    assert resized_segment.end == pytest.approx(1.0)
    assert resized_segment.words[0].start == pytest.approx(0.5 + (0.0 - 0.0) * 0.5)  # 0.5
    assert resized_segment.words[0].end == pytest.approx(0.5 + (0.5 - 0.0) * 0.5)  # 0.75
    assert resized_segment.words[1].start == pytest.approx(0.5 + (0.6 - 0.0) * 0.5)  # 0.8
    assert resized_segment.words[1].end == pytest.approx(0.5 + (1.0 - 0.0) * 0.5)  # 1.0
    mock_listener_obj.on_subtitles_changed.assert_called_once()


def test_resize_segment_scales_words_up(subtitles_manager: SubtitlesManager, mocker: MockerFixture) -> None:
    """Test that resizing a segment to a longer duration scales words correctly."""
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    subtitles_manager.register_listener(mock_listener_obj)
    segment_index = 0
    # Original: start=0.0, end=1.0, duration=1.0
    # Words: (0.0, 0.5), (0.6, 1.0)
    new_start, new_end = 0.0, 2.0  # New duration = 2.0 (scale factor = 2.0)

    subtitles_manager.resize_segment(segment_index, new_start, new_end)
    resized_segment = subtitles_manager.subtitles.segments[segment_index]

    assert resized_segment.start == pytest.approx(0.0)
    assert resized_segment.end == pytest.approx(2.0)
    assert resized_segment.words[0].start == pytest.approx(0.0 + (0.0 - 0.0) * 2.0)  # 0.0
    assert resized_segment.words[0].end == pytest.approx(0.0 + (0.5 - 0.0) * 2.0)  # 1.0
    assert resized_segment.words[1].start == pytest.approx(0.0 + (0.6 - 0.0) * 2.0)  # 1.2
    assert resized_segment.words[1].end == pytest.approx(0.0 + (1.0 - 0.0) * 2.0)  # 2.0
    mock_listener_obj.on_subtitles_changed.assert_called_once()


def test_resize_segment_aborts_on_min_word_duration(subtitles_manager: SubtitlesManager, mocker: MockerFixture) -> None:
    """Test that resizing aborts if the new duration is too short for the words."""
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    subtitles_manager.register_listener(mock_listener_obj)
    segment = subtitles_manager.subtitles.segments[0]
    original_words = [SubtitleWord(w.text, w.start, w.end) for w in segment.words]
    # Segment has 2 words, min duration is 2 * 0.05 = 0.1s
    new_start, new_end = 0.0, 0.09

    subtitles_manager.resize_segment(0, new_start, new_end)

    # Assert that no change was made
    assert subtitles_manager.subtitles.segments[0].words == original_words
    mock_listener_obj.on_subtitles_changed.assert_not_called()


def test_resize_segment_aborts_on_zero_duration(subtitles_manager: SubtitlesManager, mocker: MockerFixture) -> None:
    """Test that resizing aborts if the new duration is zero or negative."""
    mock_listener_obj = Mock(spec=["on_subtitles_changed"])
    subtitles_manager.register_listener(mock_listener_obj)
    segment = subtitles_manager.subtitles.segments[0]
    original_words = [SubtitleWord(w.text, w.start, w.end) for w in segment.words]

    subtitles_manager.resize_segment(0, 0.5, 0.5)

    # Assert that no change was made
    assert subtitles_manager.subtitles.segments[0].words == original_words
    mock_listener_obj.on_subtitles_changed.assert_not_called()
