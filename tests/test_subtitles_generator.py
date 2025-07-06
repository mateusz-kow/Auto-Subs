import os
import unittest

from src.utils.ffmpeg_utils import get_video_with_subtitles
from tests.utils import INPUT_DIR, OUTPUT_DIR


class TestSubtitlesGenerator(unittest.TestCase):
    def setUp(self):
        self.video_path = os.path.join(INPUT_DIR, "video1.mp4")
        self.ass_path = os.path.join(OUTPUT_DIR, "test_ass_file_generator.ass")
        self.output_path = os.path.join(OUTPUT_DIR, "new_video1.mp4")

    def test_burn_subtitles_with_ffmpeg(self):

        get_video_with_subtitles(self.video_path, self.ass_path, self.output_path)

        self.assertTrue(os.path.exists(self.output_path))


if __name__ == "__main__":
    unittest.main()
