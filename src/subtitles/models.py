
from src.subtitles.segmenter import segment_words


class SubtitleWord:
    """Represents a single word in a subtitle with its text and timing."""

    def __init__(self, text: str, start: float, end: float):
        """
        Initialize a SubtitleWord instance.

        Args:
            text (str): The word text.
            start (float): The start time of the word in seconds.
            end (float): The end time of the word in seconds.
        """
        self.text = text.strip()
        self.start = start
        self.end = end

    @classmethod
    def empty(cls) -> "SubtitleWord":
        """Create an empty SubtitleWord instance."""
        return cls("", 0, 0)

    def __eq__(self, other: object) -> bool:
        """Check equality between two SubtitleWord instances."""
        if not isinstance(other, SubtitleWord):
            return False
        return self.text == other.text and self.start == other.start and self.end == other.end


class SubtitleSegment:
    """Represents a segment of subtitles containing multiple words."""

    def __init__(self, words: list[SubtitleWord]):
        """
        Initialize a SubtitleSegment instance.

        Args:
            words (List[SubtitleWord]): A list of SubtitleWord instances.
        """
        self.end: float = 0
        self.start: float = 0
        self.words: list[SubtitleWord] = words
        self.refresh()

    @classmethod
    def empty(cls) -> "SubtitleSegment":
        """Create an empty SubtitleSegment instance."""
        return cls([])

    def __str__(self) -> str:
        """Return the segment as a string of concatenated word texts."""
        return " ".join(word.text for word in self.words)

    def __eq__(self, other: object) -> bool:
        """Check equality between two SubtitleSegment instances."""
        if not isinstance(other, SubtitleSegment):
            return False
        return self.words == other.words

    def add_word(self, word: SubtitleWord = None) -> None:
        """
        Add a word to the segment.

        Args:
            word (SubtitleWord, optional): The word to add. Defaults to an empty word.
        """
        if word is None:
            word = SubtitleWord.empty()
        self.words.append(word)
        self.refresh()

    def refresh(self) -> None:
        """Refresh the segment's start and end times based on its words."""
        self.words.sort(key=lambda w: (w.start, w.end))
        if self.words:
            self.start = self.words[0].start
            self.end = self.words[-1].end
        else:
            self.start = self.end = 0


class Subtitles:
    """Represents a collection of subtitle segments."""

    def __init__(self, segments: list[SubtitleSegment]):
        """
        Initialize a Subtitles instance.

        Args:
            segments (List[SubtitleSegment]): A list of SubtitleSegment instances.
        """
        self.segments = segments

    @classmethod
    def empty(cls) -> "Subtitles":
        """Create an empty Subtitles instance."""
        return cls([])

    @classmethod
    def from_transcription(cls, transcription: dict) -> "Subtitles":
        """
        Create a Subtitles instance from a transcription dictionary.

        Args:
            transcription (dict): The transcription data.

        Returns:
            Subtitles: A Subtitles instance created from the transcription.
        """
        dict_segments = segment_words(transcription)
        segments = [
            SubtitleSegment([SubtitleWord(w["word"], w["start"], w["end"]) for w in dict_segment["words"]])
            for dict_segment in dict_segments
        ]
        return cls(segments)

    def __str__(self) -> str:
        """Return the subtitles as a string of concatenated segments."""
        return "\n".join(str(segment) for segment in self.segments)

    def add_segment(self, new_segment: SubtitleSegment = None) -> None:
        """
        Add a new segment to the subtitles.

        Args:
            new_segment (SubtitleSegment, optional): The segment to add. Defaults to an empty segment.
        """
        if new_segment is None:
            new_segment = SubtitleSegment.empty()
        self.segments.append(new_segment)
        self.refresh()

    def refresh(self) -> None:
        """Refresh the subtitles by sorting segments based on their timing."""
        self.segments.sort(key=lambda segment: (segment.start, segment.end))
