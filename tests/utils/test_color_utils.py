import unittest

from PySide6.QtGui import QColor

from src.utils.color_operations import ass_to_qcolor, qcolor_to_ass


class TestColorConversion(unittest.TestCase):
    """Unit tests for ASS <-> QColor conversion functions."""

    def test_ass_to_qcolor(self) -> None:
        """Test conversion from ASS hexadecimal color string to QColor."""
        self.assertEqual(ass_to_qcolor("&H00FFFFFF"), QColor(255, 255, 255), "White color conversion failed")
        self.assertEqual(ass_to_qcolor("&H00000000"), QColor(0, 0, 0), "Black color conversion failed")
        self.assertEqual(ass_to_qcolor("&H000000FF"), QColor(255, 0, 0), "Red color conversion failed")
        self.assertEqual(ass_to_qcolor("&H0000FF00"), QColor(0, 255, 0), "Green color conversion failed")
        self.assertEqual(ass_to_qcolor("&H00FF0000"), QColor(0, 0, 255), "Blue color conversion failed")

    def test_qcolor_to_ass(self) -> None:
        """Test conversion from QColor to ASS hexadecimal color string."""
        self.assertEqual(qcolor_to_ass(QColor(255, 255, 255)), "&H00FFFFFF", "White conversion to ASS failed")
        self.assertEqual(qcolor_to_ass(QColor(0, 0, 0)), "&H00000000", "Black conversion to ASS failed")
        self.assertEqual(qcolor_to_ass(QColor(255, 0, 0)), "&H000000FF", "Red conversion to ASS failed")
        self.assertEqual(qcolor_to_ass(QColor(0, 255, 0)), "&H0000FF00", "Green conversion to ASS failed")

        blue_with_alpha = QColor(0, 0, 255)
        blue_with_alpha.setAlpha(245)
        self.assertEqual(qcolor_to_ass(blue_with_alpha), "&H0AFF0000", "Alpha-preserved blue conversion failed")

    def test_round_trip_conversion(self) -> None:
        """Test that QColor -> ASS -> QColor round-trip conversion preserves color and alpha."""
        test_colors = [
            QColor(255, 255, 255),  # White
            QColor(128, 64, 32),  # Arbitrary RGB
            QColor(10, 20, 30),  # Arbitrary RGB
            QColor(0, 0, 0, a=0),  # Fully transparent black
            QColor(1, 2, 3, a=123),  # Partially transparent
        ]

        for original in test_colors:
            ass_code = qcolor_to_ass(original)
            converted = ass_to_qcolor(ass_code)
            self.assertEqual(
                original,
                converted,
                f"Round-trip failed: original={original.getRgb()}, ass='{ass_code}', converted={converted.getRgb()}",
            )


if __name__ == "__main__":
    unittest.main()
