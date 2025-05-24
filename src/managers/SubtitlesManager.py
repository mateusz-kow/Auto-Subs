import asyncio
from src.subtitles.models import Subtitles, SubtitleSegment, SubtitleWord


class SubtitlesManager:
    """Manages subtitle operations and notifies listeners of changes."""

    def __init__(self, subtitles: Subtitles = None):
        self._subtitles = subtitles
        self._subtitles_listeners = []

    def set_subtitles(self, subtitles: Subtitles):
        """Set the current subtitles and notify listeners."""
        self._subtitles = subtitles
        self._notify_listeners()

    def add_subtitles_listener(self, listener):
        """Register a listener to be notified of subtitle changes."""
        self._subtitles_listeners.append(listener)

    def delete_word(self, segment_index, word_index):
        """Delete a word from a specific segment."""
        del self._subtitles.segments[segment_index].words[word_index]
        self._refresh_segment(segment_index)

    def delete_segments(self, segments_indexes: list[int]):
        """Delete multiple segments by their indexes."""
        for index in sorted(segments_indexes, reverse=True):
            del self._subtitles.segments[index]
        self._refresh_subtitles()

    def add_empty_segment(self):
        """Add an empty segment if it doesn't already exist."""
        if not self._subtitles.segments or self._subtitles.segments[0] != SubtitleSegment.empty():
            self._subtitles.segments.append(SubtitleSegment.empty())
            self._refresh_subtitles()

    def add_word_to_segment(self, segment_index: int, word: SubtitleWord):
        """Add a word to a specific segment."""
        self._subtitles.segments[segment_index].words.append(word)
        self._refresh_segment(segment_index)

    def merge_segments(self, segment_indices: list[int]):
        """Merge multiple segments into one."""
        if not segment_indices:
            return

        first_index = min(segment_indices)
        last_index = max(segment_indices)

        if first_index == last_index:
            return

        words = []
        for index in sorted(segment_indices, reverse=True):
            words.extend(self._subtitles.segments[index].words)
            del self._subtitles.segments[index]

        merged_segment = SubtitleSegment(words=words)
        self.subtitles.add_segment(merged_segment)
        self._notify_listeners()

    def set_word(self, segment_index: int, word_index: int, word: SubtitleWord):
        """Update a word in a specific segment."""
        segment = self._subtitles.segments[segment_index]
        if segment.words[word_index] != word:
            segment.words[word_index] = word
            self._refresh_segment(segment_index)

    def add_empty_word(self, segment_index: int):
        """Add an empty word to a specific segment."""
        segment = self._subtitles.segments[segment_index]
        if not segment.words or segment.words[0] != SubtitleWord("", 0, 0):
            segment.words.append(SubtitleWord("", 0, 0))
            self._refresh_segment(segment_index)

    def on_transcription_changed(self, transcription):
        """Update subtitles based on transcription changes."""

        async def task():
            self._subtitles = await asyncio.to_thread(Subtitles.from_transcription, transcription)
            self._notify_listeners()

        asyncio.create_task(task())

    def on_video_changed(self, video_path):
        self._subtitles = Subtitles.empty()

    def _refresh_segment(self, segment_index: int):
        """Refresh a specific segment and notify listeners."""
        self._subtitles.segments[segment_index].refresh()
        self._notify_listeners()

    def _refresh_subtitles(self):
        """Refresh all subtitles and notify listeners."""
        self._subtitles.refresh()
        self._notify_listeners()

    def _notify_listeners(self):
        """Notify all registered listeners of subtitle changes."""
        for listener in self._subtitles_listeners:
            listener(self._subtitles)

    @property
    def subtitles(self):
        return self._subtitles
