"""Tests for the Phase 3 animatic builder (deterministic parts only).

Covers grid parsing, column-major panel slicing, and dialogue extraction —
no ffmpeg/TTS calls (those need a display/encoder and are exercised manually).
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import build_animatic as ba  # noqa: E402


class TestGridParse(unittest.TestCase):
    def test_standard(self):
        self.assertEqual(ba._parse_grid("3x2"), (3, 2))
        self.assertEqual(ba._parse_grid("2x3"), (2, 3))

    def test_default_on_blank(self):
        self.assertEqual(ba._parse_grid(""), (3, 2))
        self.assertEqual(ba._parse_grid(None), (3, 2))


class TestDialogueExtract(unittest.TestCase):
    def test_quoted_lines(self):
        self.assertEqual(
            ba._extract_dialogue('char_01: "Mama!", char_02: "Hi there"'),
            ["Mama!", "Hi there"],
        )

    def test_empty(self):
        self.assertEqual(ba._extract_dialogue(""), [])
        self.assertEqual(ba._extract_dialogue(None), [])


@unittest.skipUnless(ba.Image is not None, "Pillow not installed")
class TestSliceSheet(unittest.TestCase):
    def _make_sheet(self, path: str, w: int = 600, h: int = 600):
        from PIL import Image
        # solid colour quadrants so we can verify crop coordinates
        im = Image.new("RGB", (w, h), (10, 10, 10))
        im.save(path)

    def test_column_major_numbering(self):
        with tempfile.TemporaryDirectory() as d:
            sheet = os.path.join(d, "sheet.png")
            self._make_sheet(sheet, w=200, h=300)  # 2 cols x 3 rows
            panels = ba.slice_sheet(sheet, "3x2", os.path.join(d, "out"))
            # 3 rows x 2 cols = 6 panels, returned ordered by panel number
            self.assertEqual(len(panels), 6)
            self.assertTrue(all(os.path.isfile(p) for p in panels))
            from PIL import Image
            with Image.open(panels[0]) as p1:
                # each panel is width/2 by height/3
                self.assertEqual(p1.size, (100, 100))

    def test_grid_respected(self):
        with tempfile.TemporaryDirectory() as d:
            sheet = os.path.join(d, "sheet.png")
            self._make_sheet(sheet, w=400, h=200)  # 2x2
            panels = ba.slice_sheet(sheet, "2x2", os.path.join(d, "out"))
            self.assertEqual(len(panels), 4)
            from PIL import Image
            with Image.open(panels[0]) as p1:
                self.assertEqual(p1.size, (200, 100))


if __name__ == "__main__":
    unittest.main()
