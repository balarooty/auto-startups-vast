"""P2 tests — voice bible schema, coverage, distinctness (cover-up-names test)."""

from __future__ import annotations

import os
import sys
import textwrap
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import validators  # noqa: E402

BIBLE = textwrap.dedent("""\
    # Voice Bible — Test Episode

    ## Character: char_01
    voice_description: mid-pitched, gravelly, unhurried coastal drawl
    speech_pattern: short clipped fragments, drops subjects, never asks two questions in one breath
    signature_vocabulary: flame-tender, batch o' gold
    taboos: never says please when demanding
    sample_lines:
    - "Fire's hot. Dough's pleated. Another batch o' gold."
    - "Paws off, gutter-prowler!"
    registers:
      toward_char_02: sharp but secretly fond

    ## Character: char_02
    voice_description: bright, quick, sing-song up-talking
    speech_pattern: breathless run-ons that tumble over themselves, ends on a challenge
    signature_vocabulary: mine now, slowpoke
    taboos: never apologizes first
    sample_lines:
    - "Mine now, slowpoke!"
    - "Three coppers?! You're a bandit, Old Man!"
    registers:
      toward_char_01: cheeky defiance with real respect underneath
""")


def _scenes():
    return {"scenes": [
        {"scene_id": "s1", "cast": ["char_01", "char_02"]},
    ]}


class TestVoiceBible(unittest.TestCase):
    def test_valid_bible_passes(self):
        res = validators.validate_voice_bible(BIBLE, scenes=_scenes())
        self.assertTrue(res.ok, res.errors)

    def test_missing_field_errors(self):
        bad = BIBLE.replace("signature_vocabulary: flame-tender, batch o' gold\n", "")
        res = validators.validate_voice_bible(bad, scenes=_scenes())
        self.assertFalse(res.ok)
        self.assertTrue(any("missing 'signature_vocabulary" in e for e in res.errors), res.errors)

    def test_missing_cast_entry_errors(self):
        scenes = {"scenes": [{"scene_id": "s1", "cast": ["char_01", "char_02", "char_03"]}]}
        res = validators.validate_voice_bible(BIBLE, scenes=scenes)
        self.assertFalse(res.ok)
        self.assertTrue(any("no entry for cast character char_03" in e for e in res.errors), res.errors)

    def test_unknown_character_warns(self):
        scenes = {"scenes": [{"scene_id": "s1", "cast": ["char_01"]}]}
        res = validators.validate_voice_bible(BIBLE, scenes=scenes)
        self.assertTrue(any("char_02: not in any scene's cast" in w for w in res.warnings), res.warnings)

    def test_identical_speech_patterns_warn(self):
        same = (
            "short clipped fragments, drops subjects, never asks two questions in one breath"
        )
        bad = BIBLE.replace(
            "speech_pattern: breathless run-ons that tumble over themselves, ends on a challenge",
            f"speech_pattern: {same}",
        )
        res = validators.validate_voice_bible(bad, scenes=_scenes())
        self.assertTrue(any("near-identical" in w and "cover-up-names" in w
                            for w in res.warnings), res.warnings)

    def test_bad_sample_line_warns(self):
        bad = BIBLE.replace(
            '- "Fire\'s hot. Dough\'s pleated. Another batch o\' gold."',
            '- "<d>[English] ...</d>"',
        )
        res = validators.validate_voice_bible(bad, scenes=_scenes())
        self.assertTrue(any("sample line issue" in w for w in res.warnings), res.warnings)

    def test_no_entries_errors(self):
        res = validators.validate_voice_bible("# empty bible\n")
        self.assertFalse(res.ok)
        self.assertTrue(any("no '## Character" in e for e in res.errors), res.errors)


if __name__ == "__main__":
    unittest.main()
