import unittest
import os
from src.utils.ffmpeg_utils import get_preview_image
from tests.utils import INPUT_DIR, OUTPUT_DIR


class TestSubtitlePreviewGenerator(unittest.TestCase):
    def setUp(self):
        self.video_path = os.path.join(INPUT_DIR, "video1.mp4")
        self.ass_path = os.path.join(OUTPUT_DIR, "test_ass_file_generator.ass")
        self.output_path = os.path.join(OUTPUT_DIR, "preview_frame.jpg")

        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
        if not os.path.exists(self.ass_path):
            raise FileNotFoundError(f"ASS file not found: {self.ass_path}")

    def test_generate_preview_jpg(self):
        result_path = get_preview_image(
            self.video_path, self.ass_path, self.output_path
        )
        self.assertTrue(os.path.exists(result_path), "Preview image was not generated.")


if __name__ == "__main__":
    unittest.main()
