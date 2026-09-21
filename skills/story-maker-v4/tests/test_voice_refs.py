"""P4 tests — per-character voice reference resolution (deterministic parts)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import render_all  # noqa: E402


def _gen(dialogues: list[str], chars: list[list[str]]) -> dict:
    return {
        "gen_id": "g1",
        "shots": [
            {"shot": i + 1, "dialogue": d, "characters_present": c}
            for i, (d, c) in enumerate(zip(dialogues, chars))
        ],
    }


class TestVoiceRefs(unittest.TestCase):
    def test_resolves_voice_clips_for_speaking_characters(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = os.path.join(d, "epi-1")
            os.makedirs(os.path.join(d, "assets", "voices"))
            with open(os.path.join(d, "assets", "voices", "char_01.wav"), "wb") as f:
                f.write(b"RIFF")
            gen = _gen(['char_01: "Hi"', ""], [["char_01"], ["char_01"]])
            refs = render_all._find_voice_refs(run_dir, gen)
            self.assertEqual(len(refs), 1)
            self.assertTrue(refs[0].endswith("char_01.wav"))

    def test_skips_non_speaking_characters(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = os.path.join(d, "epi-1")
            os.makedirs(os.path.join(d, "assets", "voices"))
            with open(os.path.join(d, "assets", "voices", "char_01.wav"), "wb") as f:
                f.write(b"RIFF")
            with open(os.path.join(d, "assets", "voices", "char_02.wav"), "wb") as f:
                f.write(b"RIFF")
            gen = _gen(['char_01: "Hi"'], [["char_01", "char_02"]])
            refs = render_all._find_voice_refs(run_dir, gen)
            # only the speaker is attached, not the silent co-present character
            self.assertEqual(len(refs), 1)

    def test_no_voices_dir_returns_none(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = os.path.join(d, "epi-1")
            os.makedirs(run_dir)
            gen = _gen(['Pip (S1): "Hi"'], [["char_01"]])
            self.assertIsNone(render_all._find_voice_refs(run_dir, gen))

    def test_dialogue_none_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            run_dir = os.path.join(d, "epi-1")
            os.makedirs(os.path.join(d, "assets", "voices"))
            with open(os.path.join(d, "assets", "voices", "char_01.wav"), "wb") as f:
                f.write(b"RIFF")
            gen = _gen(["none"], [["char_01"]])
            self.assertIsNone(render_all._find_voice_refs(run_dir, gen))


if __name__ == "__main__":
    unittest.main()
