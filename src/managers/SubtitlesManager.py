from src.subtitles.models import Subtitles, SubtitleSegment, SubtitleWord
from src.subtitles.generator import SubtitleGenerator


class SubtitlesManager:
    def __init__(self, subtitles: Subtitles = None):
        self.subtitles = subtitles
        self.subtitles_listeners = []

    def export_ass(self, ass_settings: dict, path: str = None):
        return SubtitleGenerator.to_ass(self.subtitles, ass_settings, output_path=path)

    def export_srt(self, path: str = None):
        return SubtitleGenerator.to_srt(self.subtitles, output_path=path)

    def set_subtitles(self, subtitles: Subtitles):
        self.subtitles = subtitles

        for listener in self.subtitles_listeners:
            listener(subtitles)

    def add_subtitles_listener(self, listener):
        self.subtitles_listeners.append(listener)

    def delete_word(self, segment_index, word_index):
        # Get the segment by index
        segment = self.subtitles.segments[segment_index]

        # Remove the word at the specified index
        del segment.words[word_index]

        # Refresh the segment to update its state
        segment.refresh()

        # Notify all listeners about the updated subtitles
        for listener in self.subtitles_listeners:
            listener(self.subtitles)

    def delete_segments(self, segments_indexes):
        # Sort the indexes in descending order to avoid index shifting
        sorted_indexes = sorted(segments_indexes, reverse=True)

        # Remove segments at the specified indexes
        for index in sorted_indexes:
            del self.subtitles.segments[index]

        # Refresh the subtitles to update their state
        self.subtitles.refresh()

        # Notify all listeners about the updated subtitles
        for listener in self.subtitles_listeners:
            listener(self.subtitles)

    def add_empty_segment(self):
        segment = SubtitleSegment.empty()

        if self.subtitles.segments and self.subtitles.segments[0] == segment:
            return

        self.subtitles.segments.append(segment)
        self.subtitles.refresh()

        for listener in self.subtitles_listeners:
            listener(self.subtitles)

    def add_word_to_segment(self, segment_index: int, word: SubtitleWord):
        # Get the segment by index
        segment = self.subtitles.segments[segment_index]

        # Add the word to the segment
        segment.words.append(word)

        # Refresh the segment to update its state
        segment.refresh()

        # Notify all listeners about the updated subtitles
        for listener in self.subtitles_listeners:
            listener(self.subtitles)

    def set_word(self, segment_index: int, word_index: int, word: SubtitleWord):
        # Get the segment by index
        segment = self.subtitles.segments[segment_index]

        # Update the word at the specified index
        if segment.words[word_index] == word:
            return

        segment.words[word_index] = word

        # Refresh the segment to update its state
        segment.refresh()
        self.subtitles.refresh()

        # Notify all listeners about the updated subtitles
        for listener in self.subtitles_listeners:
            listener(self.subtitles)

    def add_empty_word(self, segment_index: int):
        # Get the segment by index
        segment = self.subtitles.segments[segment_index]

        # Add an empty word to the segment
        empty_word = SubtitleWord("", 0, 0)
        if len(segment.words) > 0 and segment.words[0] == empty_word:
            return
        segment.words.append(empty_word)

        # Refresh the segment to update its state
        segment.refresh()

        # Notify all listeners about the updated subtitles
        for listener in self.subtitles_listeners:
            listener(self.subtitles)

    def on_transcription_changed(self, transcription):
        """
        Called when the transcription changes. Can be used to update the subtitles.
        """
        self.subtitles = Subtitles.from_transcription(transcription)

        # Notify all listeners about the updated subtitles
        for listener in self.subtitles_listeners:
            listener(self.subtitles)


