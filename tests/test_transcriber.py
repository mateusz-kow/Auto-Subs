import os
import unittest
from src.managers.TranscriptionManager import TranscriptionManager
from tests.utils import INPUT_DIR, OUTPUT_DIR
import json


class TestWhisperTranscriber(unittest.TestCase):
    def setUp(self):
        self.input_path = os.path.join(INPUT_DIR, "video1.mp4")
        self.word_timestamps = True
        self.transcriber = TranscriptionManager()

        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Input test file not found: {self.input_path}")

    def test_transcription_and_ass_generation(self):
        result = self.transcriber.transcribe(
            self.input_path, word_timestamps=self.word_timestamps
        )
        with open(os.path.join(OUTPUT_DIR, "transcription1.json"), "w") as file:
            json.dump(result, file, indent="\t")


if __name__ == "__main__":
    unittest.main()
