import os
import unittest
from src.subtitles.segmenter import segment_words
from tests.utils import INPUT_DIR, OUTPUT_DIR
import json


class TestSegmentation(unittest.TestCase):
    def setUp(self):
        self.input_path = os.path.join(INPUT_DIR, "transcription1.json")
        self.word_timestamps = True

        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Input test file not found: {self.input_path}")

    def test_segmentation(self):
        with open(self.input_path, "r") as file:
            transcription = json.load(file)

        result = segment_words(transcription)
        with open(os.path.join(OUTPUT_DIR, "segmentation1.json"), "w") as file:
            json.dump(result, file, indent="\t")


if __name__ == "__main__":
    unittest.main()
