"""P1 dialogue-lint tests — empty tags, vocalizations, duplicates, fit, ranking."""

from __future__ import annotations

import os
import sys
import textwrap
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import validators  # noqa: E402


def _sb():
    md = textwrap.dedent("""
        # Scene s1 — Test
        scene_id: s1
        target_seconds: 8
        cast: [char_01]
        location_ref_id: loc_x

        ## Generation g1 — 0.0-8.0s
        duration_seconds: 8.0
        panel_grid: 2x3

        ### Shot 1 — 0.0-4.0s (continuous)
        panels: [1, 2, 3]
        characters_present: [char_01]
        shot_size: medium
        composition: center
        acting_beat: a → b
        layout: fg/mg/bg
        screen_direction: held
        action: The character calls out across the yard.
        camera: Static Shot.
        audio: wind
        dialogue: char_01: "Hello out there"

        ### Shot 2 — 4.0-8.0s (continuous)
        panels: [4, 5, 6]
        characters_present: [char_01]
        shot_size: closeup
        composition: center
        acting_beat: c → d
        layout: face center
        screen_direction: held
        action: The character listens, then grins.
        camera: Static Shot.
        audio: breeze
        dialogue:

        ## Scene-end handoff -> scene end
        on_screen: [char_01]
        mood: calm
        transition: hard_cut
    """).strip()
    return validators.parse_storyboard(md)


AUDIO = textwrap.dedent("""\
    Audio:
    - diegetic_dialogue: Pip (S1) calls out, <d>[English] __LINE__</d>
    - foley_and_sfx: Cloth rustle.
    - environmental_ambience: Wind over the yard, dialogue forward.
    - non_diegetic_music: Light strings, slow.""")

_SILENT_AUDIO = textwrap.dedent("""\
    Audio:
    - diegetic_dialogue: None
    - foley_and_sfx: Cloth rustle.
    - environmental_ambience: Wind.
    - non_diegetic_music: Light strings, slow.""")

_TEMPLATE = textwrap.dedent("""\
    subject_definitions:Reference

    Use the provided storyboard as the exact visual guide.

    Maintain the exact appearance of Pip: small round face, red cap.

    A windy yard at noon.

    Generate a cinematic 8.0-second sequence matching the storyboard.
    Hand-painted 2D animation with clean line work.

    Timeline

    SHOT 1 — 0.0–4.0s (Continuous Shot)

    Pip steps into the yard and calls out.
    The camera holds a static medium shot with small amplitude at slow speed.
    __AUDIO1__
    Cut on the action.

    SHOT 2 — 4.0–8.0s (Continuous Shot)

    Pip listens, then grins. __SHOT2DLG__
    The camera holds a static closeup with small amplitude at slow speed.
    __AUDIO2__""")


def _prompt(shot1_line: str = "Hello out there", shot2_line: str = "",
            *, rank: bool = True) -> str:
    a1 = AUDIO.replace("__LINE__", shot1_line)
    if not rank:
        a1 = a1.replace(", dialogue forward", "")
    if shot2_line:
        a2 = AUDIO.replace("__LINE__", shot2_line)
        shot2_dlg = f"Pip (S1) says, <d>[English] {shot2_line}</d>"
    else:
        a2 = _SILENT_AUDIO
        shot2_dlg = ""
    out = _TEMPLATE.replace("__AUDIO1__", a1)
    out = out.replace("__AUDIO2__", a2)
    out = out.replace("__SHOT2DLG__", shot2_dlg)
    return out.strip()


class TestDialogueTagLint(unittest.TestCase):
    def test_lint_empty_tag(self):
        errs = validators.lint_dialogue_tag("...")
        self.assertTrue(any("empty/placeholder" in e for e in errs))

    def test_lint_empty_tag_whitespace(self):
        self.assertTrue(validators.lint_dialogue_tag("   "))

    def test_lint_bracketed_sound(self):
        errs = validators.lint_dialogue_tag("[Gasp!]")
        self.assertTrue(any("SPOKEN" in e for e in errs))

    def test_lint_clean_line_passes(self):
        self.assertEqual(validators.lint_dialogue_tag("Hello out there"), [])


class TestVideoPromptDialogue(unittest.TestCase):
    def test_baseline_passes(self):
        res = validators.validate_video_prompt(_prompt(), _sb(), "g1")
        self.assertTrue(res.ok, res.errors)

    def test_empty_dialogue_tag_errors(self):
        res = validators.validate_video_prompt(_prompt(shot1_line="..."), _sb(), "g1")
        self.assertFalse(res.ok)
        self.assertTrue(any("empty/placeholder" in e for e in res.errors), res.errors)

    def test_gasp_in_tag_errors(self):
        res = validators.validate_video_prompt(_prompt(shot1_line="[Gasp!]"), _sb(), "g1")
        self.assertFalse(res.ok)
        self.assertTrue(any("SPOKEN" in e for e in res.errors), res.errors)

    def test_duplicate_line_errors(self):
        res = validators.validate_video_prompt(
            _prompt(shot2_line="Hello out there"), _sb(), "g1")
        self.assertFalse(res.ok)
        self.assertTrue(any("already used in SHOT" in e for e in res.errors), res.errors)

    def test_word_rate_fit_errors(self):
        long_line = " ".join(["word"] * 20)  # 20 words in a 4s shot = 5 wps
        res = validators.validate_video_prompt(_prompt(shot1_line=long_line), _sb(), "g1")
        self.assertFalse(res.ok)
        self.assertTrue(any("words/sec" in e for e in res.errors), res.errors)

    def test_missing_ranking_warns(self):
        res = validators.validate_video_prompt(_prompt(rank=False), _sb(), "g1")
        self.assertTrue(any("ranks it" in w for w in res.warnings), res.warnings)

    def test_cross_cut_repetition_warns(self):
        res = validators.validate_video_prompt(
            _prompt(shot1_line="Give it back now", shot2_line="Give it back please"),
            _sb(), "g1")
        self.assertTrue(any("near-repeats" in w for w in res.warnings), res.warnings)

    def test_voiceover_exact_phrase_and_closed_lips(self):
        # Good voiceover
        good_dlg = "Narrator (S1) says in an off-screen voiceover: <d>[English] Long ago.</d> while lips remain closed."
        p = _prompt().replace("Pip (S1) calls out, <d>[English] Hello out there</d>", good_dlg)
        res = validators.validate_video_prompt(p, _sb(), "g1")
        self.assertTrue(res.ok, res.errors)

        # Bad voiceover - wrong phrase
        bad_phrase = "Narrator (S1) speaks in warm voiceover, <d>[English] Long ago.</d> while lips remain closed."
        p_bad1 = _prompt().replace("Pip (S1) calls out, <d>[English] Hello out there</d>", bad_phrase)
        res_bad1 = validators.validate_video_prompt(p_bad1, _sb(), "g1")
        self.assertFalse(res_bad1.ok)
        self.assertTrue(any("says in an off-screen voiceover" in e for e in res_bad1.errors), res_bad1.errors)

        # Bad voiceover - missing closed lips
        bad_lips = "Narrator (S1) says in an off-screen voiceover: <d>[English] Long ago.</d>"
        p_bad2 = _prompt().replace("Pip (S1) calls out, <d>[English] Hello out there</d>", bad_lips)
        res_bad2 = validators.validate_video_prompt(p_bad2, _sb(), "g1")
        self.assertFalse(res_bad2.ok)
        self.assertTrue(any("lips remain closed" in e for e in res_bad2.errors), res_bad2.errors)


if __name__ == "__main__":
    unittest.main()
