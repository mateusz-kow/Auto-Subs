# src/managers/subtitles_manager.py
import asyncio
from logging import getLogger
from pathlib import Path
from typing import Any

from src.managers.base_manager import BaseManager, EventType
from src.subtitles.models import Subtitles, SubtitleSegment, SubtitleWord

logger = getLogger(__name__)


class SubtitlesEventType(EventType):
    """Defines the event types for the SubtitlesManager."""

    SUBTITLES_CHANGED = "on_subtitles_changed"


class SubtitlesManager(BaseManager[Subtitles]):
    """Manages subtitle operations and notifies listeners of changes."""

    def __init__(self, subtitles: Subtitles | None = None) -> None:
        """Initialize the SubtitlesManager."""
        super().__init__(SubtitlesEventType)
        self._subtitles: Subtitles = subtitles if subtitles else Subtitles.empty()
        logger.info(f"SubtitlesManager initialized with subtitles: {subtitles}")

    def set_subtitles(self, subtitles: Subtitles) -> None:
        """Set the current subtitles and notify listeners."""
        self._subtitles = subtitles
        logger.info("Subtitles set to: %s", subtitles)
        self._notify_listeners(subtitles, SubtitlesEventType.SUBTITLES_CHANGED)

    def delete_word(self, segment_index: int, word_index: int) -> None:
        """Delete a word from a specific segment."""
        del self._subtitles.segments[segment_index].words[word_index]
        self._refresh_segment(segment_index)

    def delete_segments(self, segments_indexes: set[int]) -> None:
        """Delete multiple segments by their indexes."""
        for index in sorted(segments_indexes, reverse=True):
            del self._subtitles.segments[index]
        self._refresh_subtitles()

    def add_empty_segment(self) -> None:
        """Add an empty segment if it doesn't already exist."""
        if not self._subtitles.segments or self._subtitles.segments[0] != SubtitleSegment.empty():
            self._subtitles.segments.append(SubtitleSegment.empty())
            self._refresh_subtitles()

    def add_word_to_segment(self, segment_index: int, word: SubtitleWord) -> None:
        """Add a word to a specific segment."""
        self._subtitles.segments[segment_index].words.append(word)
        self._refresh_segment(segment_index)

    def merge_segments(self, segment_indices: set[int]) -> None:
        """Merge multiple segments into one."""
        if not segment_indices:
            return

        first_index = min(segment_indices)
        last_index = max(segment_indices)

        if first_index == last_index:
            return

        words: list[SubtitleWord] = []
        for index in sorted(list(segment_indices), reverse=True):
            words.extend(self._subtitles.segments[index].words)
            del self._subtitles.segments[index]

        merged_segment = SubtitleSegment(words=words)
        self.subtitles.add_segment(merged_segment)
        self._notify_listeners(self._subtitles, SubtitlesEventType.SUBTITLES_CHANGED)

    def resize_segment(self, segment_index: int, new_start: float, new_end: float) -> None:
        """Resize a segment and scale its words proportionally."""
        segment = self._subtitles.segments[segment_index]
        original_start = segment.start
        original_duration = segment.end - original_start
        new_duration = new_end - new_start

        if original_duration <= 0 or new_duration <= 0:
            logger.warning("Resize resulted in zero or negative duration. Aborting.")
            return

        min_segment_duration = len(segment.words) * 0.05
        if new_duration < min_segment_duration:
            logger.warning(
                "Resize aborted. New duration %.2f is less than minimum required %.2f",
                new_duration,
                min_segment_duration,
            )
            return

        scale_factor = new_duration / original_duration

        for word in segment.words:
            start_offset = word.start - original_start
            end_offset = word.end - original_start

            word.start = new_start + (start_offset * scale_factor)
            word.end = new_start + (end_offset * scale_factor)

        self._refresh_segment(segment_index)

    def set_word(self, segment_index: int, word_index: int, word: SubtitleWord) -> None:
        """Update a word in a specific segment."""
        segment = self._subtitles.segments[segment_index]
        if segment.words[word_index] != word:
            segment.words[word_index] = word
            self._refresh_segment(segment_index)

    def add_empty_word(self, segment_index: int) -> None:
        """Add an empty word to a specific segment."""
        segment = self._subtitles.segments[segment_index]
        if not segment.words or segment.words[0] != SubtitleWord.empty():
            segment.words.append(SubtitleWord.empty())
            self._refresh_segment(segment_index)

    def on_transcription_changed(self, transcription: dict[str, Any]) -> None:
        """Update subtitles based on transcription changes."""

        async def task() -> None:
            self._subtitles = await asyncio.to_thread(Subtitles.from_transcription, transcription)
            self._notify_listeners(self._subtitles, SubtitlesEventType.SUBTITLES_CHANGED)

        asyncio.create_task(task())

    def on_video_changed(self, video_path: Path) -> None:
        """Listener for when the video changes. Clears existing subtitles."""
        self._subtitles = Subtitles.empty()
        self._notify_listeners(self._subtitles, SubtitlesEventType.SUBTITLES_CHANGED)

    def _refresh_segment(self, segment_index: int) -> None:
        """Refresh a specific segment and notify listeners."""
        self._subtitles.segments[segment_index].refresh()
        self._notify_listeners(self._subtitles, SubtitlesEventType.SUBTITLES_CHANGED)

    def _refresh_subtitles(self) -> None:
        """Refresh all subtitles and notify listeners."""
        self._subtitles.refresh()
        self._notify_listeners(self._subtitles, SubtitlesEventType.SUBTITLES_CHANGED)

    @property
    def subtitles(self) -> Subtitles:
        """Return the current Subtitles object."""
        return self._subtitles
