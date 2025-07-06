import unittest

from PySide6.QtGui import QColor

from src.utils.color_operations import ass_to_qcolor, qcolor_to_ass


class TestColorConversion(unittest.TestCase):

    def test_ass_to_qcolor(self):
        self.assertEqual(ass_to_qcolor("&H00FFFFFF"), QColor(255, 255, 255))
        self.assertEqual(ass_to_qcolor("&H00000000"), QColor(0, 0, 0))
        self.assertEqual(ass_to_qcolor("&H000000FF"), QColor(255, 0, 0))  # red
        self.assertEqual(ass_to_qcolor("&H0000FF00"), QColor(0, 255, 0))  # green
        self.assertEqual(ass_to_qcolor("&H00FF0000"), QColor(0, 0, 255))  # blue

    def test_qcolor_to_ass(self):
        self.assertEqual(qcolor_to_ass(QColor(255, 255, 255)), "&H00FFFFFF")
        self.assertEqual(qcolor_to_ass(QColor(0, 0, 0)), "&H00000000")
        self.assertEqual(qcolor_to_ass(QColor(255, 0, 0)), "&H000000FF")  # red
        self.assertEqual(qcolor_to_ass(QColor(0, 255, 0)), "&H0000FF00")  # green
        color = QColor(0, 0, 255)
        color.setAlpha(245)
        self.assertEqual(qcolor_to_ass(color), "&H0AFF0000")

    def test_round_trip_conversion(self):
        original_colors = [
            QColor(255, 255, 255),
            QColor(128, 64, 32),
            QColor(10, 20, 30),
            QColor(0, 0, 0, a=0),
            QColor(1, 2, 3, a=123),
        ]
        for color in original_colors:
            ass = qcolor_to_ass(color)
            back = ass_to_qcolor(ass)
            self.assertEqual(color, back)


if __name__ == "__main__":
    unittest.main()
