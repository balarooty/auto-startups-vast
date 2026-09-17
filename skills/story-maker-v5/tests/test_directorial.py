"""Tests for the directorial-breakdown surface: 4-stem audio, char_state,
color_script, and scripts/directorial_breakdown.py."""
import json
import os
import sys
import textwrap

from tools import validators

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))


# --- parse helpers -----------------------------------------------------------

def test_parse_char_state():
    assert validators.parse_char_state(
        "char_01=soaked, fur flat; char_02=dry"
    ) == {"char_01": "soaked, fur flat", "char_02": "dry"}
    assert validators.parse_char_state("") == {}
    assert validators.parse_char_state("garbage without equals") == {}


def test_shot_audio_text_stems_win():
    shot = {
        "audio": "flat fallback",
        "audio_dia": "gasp", "audio_fx": "splash",
        "audio_amb": "", "audio_mus": "strings swell",
    }
    assert validators.shot_audio_text(shot) == "gasp; splash; strings swell"


def test_shot_audio_text_flat_fallback():
    assert validators.shot_audio_text({"audio": "footsteps"}) == "footsteps"
    assert validators.shot_audio_text({}) == ""


# --- scenes: color_script ----------------------------------------------------

SCENES_MD = textwrap.dedent("""
    # Scenes
    target_seconds: 15
    scene_budget: 70

    ## Scene s1 — Shore
    scene_id: s1
    target_seconds: 15
    cast: [char_01]
    characters_present: [char_01]
    location_id: loc_01
    style_target: polished 3D cartoon feature animation
    acting_beat: play → panic → relief
    layout_strategy: shoreline foreground, sea midground
    visual_motif: sparkling water
    sound_world: waves, gulls
    color_script: sun-drenched golds — warmth and play
    beat: A baby plays at the sea's edge.
""").strip()


def test_scenes_parse_color_script():
    sc = validators.parse_scenes(SCENES_MD)["scenes"][0]
    assert sc["color_script"] == "sun-drenched golds — warmth and play"


def test_scenes_warn_missing_color_script():
    md = SCENES_MD.replace(
        "color_script: sun-drenched golds — warmth and play\n", "", 1)
    res = validators.validate_scenes(md, target_seconds=15)
    assert res.ok
    assert any("color_script" in w for w in res.warnings)


# --- storyboard: audio stems + char_state ------------------------------------

STORYBOARD_MD = textwrap.dedent("""
    # Scene s1 — Shore
    scene_id: s1
    target_seconds: 15
    cast: [char_01]
    location_ref_id: loc_01

    ## Generation g1 — 0.0-15.0s
    duration_seconds: 15.0
    panel_grid: 3x2

    ### Shot 1 — 0.0-7.0s (continuous)
    panels: [1, 2, 3]
    characters_present: [char_01]
    shot_size: medium
    composition: center, depth
    camera_angle: low_angle
    focus: shallow_focus
    acting_beat: splash → freeze → wide-eyed stare at the wave
    layout: baby foreground, sea midground, wave cresting background
    screen_direction: left_to_right
    action: The baby splashes at the shoreline, then freezes as a wave rises behind him.
    camera: Slow Push In.
    audio_dia: (S1) delighted giggle
    audio_fx: water splashing, tiny feet on wet sand
    audio_amb: gentle surf, distant gulls
    audio_mus: playful strings, medium tempo
    char_state: char_01=dry, banana-leaf shorts, coconut earrings
    dialogue:

    ### Shot 2 — 7.0-15.0s (audio_led)
    panels: [4, 5, 6]
    characters_present: [char_01]
    shot_size: wide
    composition: negative_space, leading_lines
    camera_angle: high_angle
    focus: deep_focus
    acting_beat: wave crash → swept off feet → dragged seaward
    layout: towering wave dominates frame, baby small against the foam
    screen_direction: right_to_left
    action: The wave smashes down and sweeps the baby off his feet into the sea.
    camera: Tilt Down with the breaking wave.
    audio_fx: roaring wave crash, churning water
    audio_amb: storm wind rising
    char_state: char_01=soaked, hair plastered flat
    dialogue: char_01: "Help!"

    ## Scene-end handoff -> scene s2
    on_screen: [char_01]
    mood: peril
    transition: hard_cut
""").strip()


def test_storyboard_parses_stems_and_char_state():
    sb = validators.parse_storyboard(STORYBOARD_MD)
    s1, s2 = sb["generations"][0]["shots"]
    assert s1["audio_dia"] == "(S1) delighted giggle"
    assert s1["audio_mus"] == "playful strings, medium tempo"
    assert s1["char_state"] == {
        "char_01": "dry, banana-leaf shorts, coconut earrings"}
    assert s2["char_state"] == {"char_01": "soaked, hair plastered flat"}


def test_storyboard_stems_pass_audio_led_without_flat_audio():
    """audio_led with only stems (no flat audio:) must not error."""
    res = validators.validate_storyboard(STORYBOARD_MD)
    assert res.ok, res.errors
    assert not [w for w in res.warnings if "audio_led" in w or "audio" in w]


def test_storyboard_warns_char_state_not_present():
    bad = STORYBOARD_MD.replace(
        "char_state: char_01=soaked, hair plastered flat",
        "char_state: char_09=soaked, hair plastered flat")
    res = validators.validate_storyboard(bad)
    assert any("char_09" in w for w in res.warnings)


def test_storyboard_warns_no_audio_planning():
    bad = STORYBOARD_MD.replace(
        "audio_fx: roaring wave crash, churning water\n", ""
    ).replace("audio_amb: storm wind rising\n", "")
    res = validators.validate_storyboard(bad)
    # shot 2 still has dialogue, so no no-audio warning for it;
    # strip dialogue too to trigger
    bad = bad.replace('dialogue: char_01: "Help!"', "dialogue:")
    res = validators.validate_storyboard(bad)
    assert any("no audio planning" in w for w in res.warnings)


# --- directorial_breakdown ---------------------------------------------------

def _write_fixture_run(run: str) -> None:
    with open(os.path.join(run, "story.json"), "w") as f:
        json.dump({
            "title": "The Baby and the Dolphin",
            "characters": [{
                "id": "char_01", "name": "Baby Boy",
                "state_changes": [
                    {"at": "s1/g1", "becomes": "dry, banana-leaf shorts"},
                    {"at": "s1/g2", "becomes": "soaked, shivering"},
                ],
            }],
            "locations": [{"id": "loc_01", "name": "Seashore"}],
            "objects": [{"id": "obj_01", "name": "Driftwood",
                         "states": ["floating", "held"]}],
            "constraints": [{"id": "H1", "type": "prop_state",
                             "severity": "BLOCKER",
                             "rule": "Driftwood lost when the big wave hits."}],
        }, f)
    with open(os.path.join(run, "developed_story.md"), "w") as f:
        f.write(textwrap.dedent("""
            # Screenplay
            ```text
            EXT. SEASHORE - DAY
            A baby splashes.
            ```
            ## Directorial Intent
            Near-silent storytelling; the sea is the antagonist.
            ## Color Script
            - s1: gold and aqua — safety
            - s2: storm grey-teal — peril
            ## Characters
            - id: char_01
        """))
    with open(os.path.join(run, "beat_board.md"), "w") as f:
        f.write(textwrap.dedent("""
            # Beat Board
            target_seconds: 15
            beat_count: 1

            ## Beat 1 — Play
            description: A baby plays at the sea's edge.
            emotion: joy
            estimated_seconds: 15
        """))
    with open(os.path.join(run, "scenes.md"), "w") as f:
        f.write(SCENES_MD)
    with open(os.path.join(run, "storyboard_s1.md"), "w") as f:
        f.write(STORYBOARD_MD)


def test_directorial_breakdown(tmp_path):
    import directorial_breakdown as db

    run = str(tmp_path)
    _write_fixture_run(run)
    text = db.build_breakdown(run)

    assert "# Directorial Breakdown — The Baby and the Dolphin" in text
    assert "Near-silent storytelling" in text
    assert "storm grey-teal" in text
    assert "dry, banana-leaf shorts" in text
    assert "char_01" in text
    assert "playful strings" in text
    assert "g1/s1" in text
    assert "soaked, hair plastered flat" in text
