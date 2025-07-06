import os
import unittest
import json

from src.subtitles.models import Subtitles, SubtitleSegment, SubtitleWord
from tests.utils import INPUT_DIR, OUTPUT_DIR


class TestSubtitleGeneration(unittest.TestCase):
    def setUp(self):
        self.input_path = os.path.join(INPUT_DIR, "video1.mp4")
        self.input_json_path = os.path.join(INPUT_DIR, "transcription1.json")
        self.word_timestamps = True

    def test_subtitles_structure_and_export(self):
        with open(self.input_json_path, "r") as file:
            transcription = json.load(file)

        subtitles = Subtitles.from_transcription(transcription)
        self.assertIsInstance(subtitles, Subtitles)
        self.assertGreater(len(subtitles.segments), 0)

        for segment in subtitles.segments:
            self.assertIsInstance(segment, SubtitleSegment)
            self.assertGreaterEqual(segment.end, segment.start)
            self.assertGreater(len(segment.words), 0)
            for word in segment.words:
                self.assertIsInstance(word, SubtitleWord)
                self.assertTrue(isinstance(word.text, str))
                self.assertGreaterEqual(word.end, word.start)

        srt_output_path = os.path.join(OUTPUT_DIR, "subtitles1.srt")
        subtitles.to_srt(output_path=srt_output_path)

        ass_output_path = os.path.join(OUTPUT_DIR, "subtitles1.ass")
        subtitles.to_ass(output_path=ass_output_path)


if __name__ == "__main__":
    unittest.main()
