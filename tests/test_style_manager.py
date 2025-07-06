import os
import unittest

from src.managers.StyleManager import DEFAULT_STYLE, StyleManager
from tests.utils import OUTPUT_DIR


class TestStyleManager(unittest.TestCase):

    def setUp(self):
        self.manager = StyleManager()
        self.manager.reset_to_default()

    def test_default_style(self):
        self.manager.reset_to_default()
        self.assertEqual(self.manager.style, DEFAULT_STYLE)

    def test_from_dict_merging(self):
        self.manager.from_dict({"font": "Courier", "font_size": 40})
        style = self.manager.style
        self.assertEqual(style["font"], "Courier")
        self.assertEqual(style["font_size"], 40)
        self.assertEqual(style["title"], "Whisper Subtitles")  # unchanged

    def test_save_and_load_from_file(self):
        # Change values
        self.manager.from_dict({"font": "Verdana", "bold": 0})
        file_path = os.path.join(OUTPUT_DIR, "style_test.json")

        # Save to file
        saved_path = self.manager.save_to_file(file_path)
        self.assertTrue(os.path.isfile(saved_path))

        # Load into another instance
        other_instance = StyleManager()
        other_instance.reset_to_default()  # Clear current changes
        other_instance.load_from_file(saved_path)

        reloaded_style = other_instance.style
        self.assertEqual(reloaded_style["font"], "Verdana")
        self.assertEqual(reloaded_style["bold"], 0)


if __name__ == "__main__":
    unittest.main()
