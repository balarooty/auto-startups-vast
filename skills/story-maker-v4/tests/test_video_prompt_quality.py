"""P1 tests — video-prompt quality checks (panel refs, 4-layer audio, budgets)."""

from __future__ import annotations

import os
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import validators  # noqa: E402


def _sb():
    """Storyboard with one 15s generation, two shots, motion_profile set."""
    md = textwrap.dedent("""
        # Scene s1 — Test
        scene_id: s1
        target_seconds: 15
        cast: [char_01]
        location_ref_id: loc_x

        ## Generation g1 — 0.0-15.0s
        duration_seconds: 15.0
        panel_grid: 2x3

        ### Shot 1 — 0.0-7.5s (continuous)
        panels: [1, 2, 3]
        characters_present: [char_01]
        shot_size: medium
        composition: rule_of_thirds
        acting_beat: still → reach → grab
        layout: hero left third, depth layers
        screen_direction: left_to_right
        motion_profile: ease_in_out, on_twos, follow_through
        action: The character reaches out and grabs the rail, coat settling after.
        camera: Tracking Shot slow.
        audio: cloth rustle, footsteps
        dialogue:

        ### Shot 2 — 7.5-15.0s (continuous)
        panels: [4, 5, 6]
        characters_present: [char_01]
        shot_size: closeup
        composition: center
        acting_beat: settle → smile
        layout: face center, soft falloff
        screen_direction: held
        motion_profile: ease_out, on_twos
        action: The character settles and smiles at the horizon.
        camera: Static Shot.
        audio: soft breeze
        dialogue:

        ## Scene-end handoff -> scene end
        on_screen: [char_01]
        mood: calm
        transition: hard_cut
    """).strip()
    return validators.parse_storyboard(md)


AUDIO_OK = textwrap.dedent("""\
    Audio:
    - diegetic_dialogue: None
    - foley_and_sfx: Cloth rustle and boots scuffing grit.
    - environmental_ambience: Wind over the ridge, distant birds.
    - non_diegetic_music: Low strings easing, slow tempo.""")

_TEMPLATE = textwrap.dedent("""\
    subject_definitions:Reference

    Use the provided storyboard as the exact visual guide for composition,
    framing, character appearance, environment, and sequence progression.

    __IDENT__

    Windswept ridge at dusk.

    Generate a cinematic 15.0-second sequence matching the storyboard.

    Hand-painted 2D animation with clean line work and flat cel shading.

    Timeline

    SHOT 1 — 0.0–7.5s (Continuous Shot)

    A medium shot opens on the character at the rail.
    The character eases into the reach, the pose holds a beat, then the hand closes and the coat settles after.
    __SHOT1BODY__
    The camera tracks slowly alongside with small amplitude at slow speed.
    __AUDIO__
    Cut on the action.

    SHOT 2 — 7.5–15.0s (Continuous Shot)

    A closeup settles on the character's face as the wind drops.
    The character eases out of the tension, the pose holds, and the shoulders lower into a soft smile.
    The camera holds a static shot.
    __AUDIO__""")


def _prompt(*, shot1_body: str = "", audio: str = AUDIO_OK,
            ident: str = "Maintain the exact appearance of Pip: small round face, red cap, green scarf.") -> str:
    """Build a Director's Brief prompt (template is pre-dedented; audio pre-indented)."""
    out = _TEMPLATE.replace("__IDENT__", ident)
    out = out.replace("__AUDIO__", audio)
    if shot1_body:
        # keep the injected sentence aligned with the surrounding prose
        out = out.replace("__SHOT1BODY__", "        " + shot1_body.strip())
    else:
        out = out.replace("        __SHOT1BODY__\n", "")
        out = out.replace("__SHOT1BODY__\n", "")
    return out.strip()



class TestP1Checks(unittest.TestCase):
    def test_baseline_prompt_passes(self):
        res = validators.validate_video_prompt(_prompt(), _sb(), "g1")
        self.assertTrue(res.ok, res.errors)

    def test_panel_reference_banned(self):
        res = validators.validate_video_prompt(
            _prompt(shot1_body="This frames the action from panel 2 of the sheet."), _sb(), "g1")
        self.assertFalse(res.ok)
        self.assertTrue(any("panel number" in e for e in res.errors), res.errors)

    def test_flat_audio_block_fails_4_layer(self):
        res = validators.validate_video_prompt(
            _prompt(audio="Audio: boots on grit, wind, low strings."), _sb(), "g1")
        self.assertFalse(res.ok)
        self.assertTrue(any("missing layer" in e for e in res.errors), res.errors)

    def test_identity_anchor_too_long_errors(self):
        long_ident = "Maintain the exact appearance of Pip: " + (" ".join(["detail"] * 130)) + "."
        res = validators.validate_video_prompt(_prompt(ident=long_ident), _sb(), "g1")
        self.assertFalse(res.ok)
        self.assertTrue(any("identity anchor" in e for e in res.errors), res.errors)

    def test_identity_anchor_medium_warns_not_errors(self):
        med = "Maintain the exact appearance of Pip: " + (" ".join(["detail"] * 70)) + "."
        res = validators.validate_video_prompt(_prompt(ident=med), _sb(), "g1")
        self.assertTrue(any("identity anchor" in w for w in res.warnings), res.warnings)

    def test_compound_camera_move_warns(self):
        res = validators.validate_video_prompt(
            _prompt(shot1_body="The camera pushes in while tilting up over the rail."), _sb(), "g1")
        self.assertTrue(any("motion path" in w for w in res.warnings), res.warnings)

    def test_explicit_primitive_decomposition_allowed(self):
        res = validators.validate_video_prompt(
            _prompt(shot1_body="The camera trucks left + pans right across the ridge."), _sb(), "g1")
        self.assertFalse(any("motion path" in w for w in res.warnings), res.warnings)

    def test_motion_profile_translation_satisfied(self):
        # Fixture expresses ease / on_twos / settles -> no motion_profile warn
        res = validators.validate_video_prompt(_prompt(), _sb(), "g1")
        self.assertFalse(any("motion_profile" in w for w in res.warnings), res.warnings)

    def test_style_contradiction_vs_style_bible_errors(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "style_bible.md"), "w") as f:
                f.write(textwrap.dedent("""
                    production_target: expressive 2D anime with cel shading
                    palette_script: cool to warm
                    shape_language: circles
                    line_weight: thin
                    background_treatment: gouache
                    lighting_rules: warm key
                    texture_grain: subtle

                    ## Palette Script
                    - scene_id: s1 | colors: blue

                    ## Do / Don't
                    - no photorealism
                """).strip())
            bad = _prompt().replace(
                "Hand-painted 2D animation with clean line work and flat cel shading.",
                "Cinematic photorealistic footage with realistic skin pores and shallow depth of field.")
            res = validators.validate_video_prompt(bad, _sb(), "g1", run_dir=d)
            self.assertFalse(res.ok)
            self.assertTrue(any("style_bible" in e for e in res.errors), res.errors)

            ok = validators.validate_video_prompt(_prompt(), _sb(), "g1", run_dir=d)
            self.assertFalse(any("style_bible" in e for e in ok.errors), ok.errors)

    def test_per_second_density_warns_on_flat_long_shot(self):
        flat = textwrap.dedent("""
            subject_definitions:Reference

            Use the provided storyboard as the exact visual guide.

            Maintain the exact appearance of Pip: small round face, red cap.

            Windswept ridge at dusk.

            Generate a cinematic 15.0-second sequence matching the storyboard.
            Hand-painted 2D animation with clean line work.

            Timeline

            SHOT 1 — 0.0–7.5s (Continuous Shot)

            The character stands at the rail while the camera tracks slowly with small amplitude at slow speed.
            Audio:
            - diegetic_dialogue: None
            - foley_and_sfx: Cloth rustle.
            - environmental_ambience: Wind over the ridge.
            - non_diegetic_music: Low strings, slow tempo.

            SHOT 2 — 7.5–15.0s (Continuous Shot)

            The character smiles.
            The character blinks once and settles.
            The camera holds a static shot.
            Audio:
            - diegetic_dialogue: None
            - foley_and_sfx: Cloth rustle.
            - environmental_ambience: Wind over the ridge.
            - non_diegetic_music: Low strings, slow tempo.
        """).strip()
        res = validators.validate_video_prompt(flat, _sb(), "g1")
        self.assertFalse(res.errors, res.errors)
        self.assertTrue(any("action sentence" in w for w in res.warnings), res.warnings)


if __name__ == "__main__":
    unittest.main()

