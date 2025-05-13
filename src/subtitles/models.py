from typing import List
from src.subtitles.segmenter import segment_words


class SubtitleWord:
    def __init__(self, text: str, start: float, end: float):
        self.text = text.strip()
        self.start = start
        self.end = end

    @classmethod
    def empty(cls):
        return cls("", 0, 0)

    def __eq__(self, other):
        return self.text == other.text and self.start == other.start and self.end == other.end


class SubtitleSegment:
    def __init__(self, words: List[SubtitleWord]):
        self.words = words
        self.start = self.words[0].start if self.words else 0
        self.end = self.words[-1].end if self.words else 0

    @classmethod
    def empty(cls):
        return cls([])

    def __str__(self):
        return " ".join(word.text for word in self.words)

    def __eq__(self, other):
        return self.words == other.words

    def add_word(self, word: SubtitleWord = None):
        if word is None:
            word = SubtitleWord("", self.start, self.start)

        self.words.append(word)
        self.refresh()

    def refresh(self):
        self.words.sort(key=lambda w: (w.start, w.end))
        if self.words:
            self.start = self.words[0].start
            self.end = self.words[-1].end
        else:
            self.start = self.end = 0


class Subtitles:
    def __init__(self, segments: List[SubtitleSegment]):
        self.segments = segments
        self.timestamps = [(word.start + word.end) / 2 for segment in self.segments for word in segment.words]

    @classmethod
    def empty(cls):
        return cls([])

    @classmethod
    def from_transcription(cls, transcription: dict):
        dict_segments = segment_words(transcription)
        segments = []
        for dict_segment in dict_segments:
            words = [SubtitleWord(w["word"], w["start"], w["end"]) for w in dict_segment["words"]]
            segments.append(SubtitleSegment(words))

        return cls(segments)

    def __str__(self):
        return "\n".join(str(segment) for segment in self.segments)

    def add_segment(self, new_segment: SubtitleSegment = None):
        if new_segment is None:
            new_segment = SubtitleSegment([])
        self.segments.append(new_segment)
        self.refresh()

    def refresh(self):
        self.segments.sort(key=lambda segment: (segment.start, segment.end))
