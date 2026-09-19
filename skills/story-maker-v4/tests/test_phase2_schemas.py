"""Tests for Phase 2 schemas: style_bible, sound_map, timing_sheet."""

from __future__ import annotations

import textwrap

from tools import validators


# --- style_bible -----------------------------------------------------------

STYLE_BIBLE = textwrap.dedent("""\
    # Style Bible — Test Episode

    production_target: expressive 2D anime with clean silhouettes
    palette_script: cool blue enclosure warming to gold
    shape_language: circles for safety, sharp angles for threat
    line_weight: thin clean outlines, bold on heroes
    background_treatment: painted gouache, soft edges
    lighting_rules: warm key from frame-left, cool fill
    texture_grain: subtle film grain, no halation

    ## Palette Script
    - scene_id: s1 | colors: cool blue, slate
    - scene_id: s2 | colors: warm gold, amber

    ## Do / Don't
    - no photorealism
    - no studio brands
""")


def test_style_bible_valid_passes():
    res = validators.validate_style_bible(STYLE_BIBLE)
    assert res.ok, res.errors


def test_style_bible_missing_field_errors():
    bad = STYLE_BIBLE.replace("line_weight: thin clean outlines, bold on heroes\n", "")
    res = validators.validate_style_bible(bad)
    assert any("line_weight" in e for e in res.errors)
    assert not res.ok


def test_style_bible_palette_scene_coverage_warns():
    scenes = {"scenes": [
        {"scene_id": "s1", "cast": ["char_01"]},
        {"scene_id": "s3", "cast": ["char_01"]},
    ]}
    res = validators.validate_style_bible(STYLE_BIBLE, scenes=scenes)
    assert any("s3" in w for w in res.warnings)


# --- sound_map -------------------------------------------------------------

SOUND_MAP = textwrap.dedent("""\
    # Sound Map — Test Episode

    ## Music Arc
    gentle intro → rising build → triumphant climax → soft button

    ## Motifs
    - char_01: bright plucky pizzicato
    - char_02: low warm cello

    ## Scene s1
    ambience: dawn birds, distant stream
    motif: char_01 pizzicato lead
    music: gentle intro theme

    ## Scene s2
    ambience: wind through trees
    motif: char_02 cello swells
    music: rising build
""")


def _scenes():
    return {"scenes": [
        {"scene_id": "s1", "cast": ["char_01"]},
        {"scene_id": "s2", "cast": ["char_02"]},
    ]}


def test_sound_map_valid_passes():
    res = validators.validate_sound_map(SOUND_MAP, scenes=_scenes())
    assert res.ok, res.errors
    assert not res.errors


def test_sound_map_missing_scene_errors():
    sm = SOUND_MAP.replace("## Scene s2", "## Scene sX")
    res = validators.validate_sound_map(sm, scenes=_scenes())
    assert any("no entry for scene s2" in e for e in res.errors)
    assert not res.ok


def test_sound_map_missing_motif_warns():
    sm = SOUND_MAP.replace("- char_02: low warm cello\n", "")
    res = validators.validate_sound_map(sm, scenes=_scenes())
    assert any("char_02" in w for w in res.warnings)


# --- timing_sheet ----------------------------------------------------------

TIMING_SHEET = textwrap.dedent("""\
    # Timing Sheet — s1 g1
    duration_seconds: 4.0

    | time | dialogue | action | camera | sound |
    |------|----------|--------|--------|-------|
    | 0.0  | -        | char enters | wide static | ambience |
    | 0.5  | "Hi there" | waves | push in | footsteps |
    | 1.5  | -        | sits | static | rustle |
    | 3.5  | -        | settle hold | static | soft tone |
""")


def test_timing_sheet_valid_passes():
    res = validators.validate_timing_sheet(TIMING_SHEET)
    assert res.ok, res.errors


def test_timing_sheet_no_rows_errors():
    res = validators.validate_timing_sheet("# empty\nno table here\n")
    assert any("no timing rows" in e for e in res.errors)
    assert not res.ok


def test_timing_sheet_dialogue_too_long_errors():
    ts = TIMING_SHEET.replace(
        '| 0.5  | "Hi there" | waves | push in | footsteps |',
        '| 0.5  | "this is a very long line that cannot fit" | waves | push in | footsteps |',
    )
    # 10 words between 0.5s and next row 1.5s = 1.0s -> 10 wps > 2.5 -> error
    res = validators.validate_timing_sheet(ts)
    assert any("words/sec" in e for e in res.errors)
    assert not res.ok


def test_timing_sheet_out_of_order_errors():
    ts = TIMING_SHEET.replace("| 1.5  |", "| 0.2  |")
    res = validators.validate_timing_sheet(ts)
    assert any("ascending" in e for e in res.errors)
    assert not res.ok
