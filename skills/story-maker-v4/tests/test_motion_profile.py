"""Tests for the per-shot `motion_profile:` animation-craft field (Phase 1).

Covers:
- MOTION_PROFILE_TERMS whitelist shape (easing / cadence / flag groups)
- unknown term -> error
- missing field -> warn
- two easings / two cadences -> error
- impact/leap action without follow_through -> warn
"""

from __future__ import annotations

import textwrap

from tools import validators


def _make_storyboard(shots_config: str) -> str:
    """Minimal valid storyboard wrapping custom shot blocks."""
    return textwrap.dedent(f"""\
        # Scene s1 — Test
        scene_id: s1
        target_seconds: 15
        cast: [char_01]
        location_ref_id: loc_test

        ## Generation g1 — 0.0-15.0s
        duration_seconds: 15.0
        panel_grid: 2x3

        ### Shot 1 — 0.0-15.0s (continuous)
        panels: [1, 2, 3, 4, 5, 6]
        characters_present: [char_01]
        shot_size: medium
        composition: center
        acting_beat: anticipation → action → reaction
        layout: readable subject silhouette over separated depth layers
        screen_direction: held
{shots_config}
        camera: Tracking Shot fast.
        audio: Footsteps.

        ## Scene-end handoff -> scene s2
        on_screen: [char_01]
        mood: tense
        transition: hard_cut
    """).strip()


def _run(shots_config: str):
    return validators.validate_storyboard(_make_storyboard(shots_config))


def test_motion_profile_terms_shape():
    # easing group
    for t in ("ease_in", "ease_out", "ease_in_out", "linear", "snap"):
        assert t in validators.MOTION_PROFILE_TERMS
    # cadence group
    for t in ("on_ones", "on_twos", "hold"):
        assert t in validators.MOTION_PROFILE_TERMS
    # principle flags
    for t in ("follow_through", "overlapping", "secondary_motion"):
        assert t in validators.MOTION_PROFILE_TERMS


def test_valid_motion_profile_accepted():
    res = _run(
        "        motion_profile: ease_in_out, on_twos, follow_through\n"
        "        action: The char leaps and lands, coat settling.\n"
    )
    assert res.ok, f"errors: {res.errors}"
    # no unknown-term errors
    assert not any("motion_profile term" in e for e in res.errors)


def test_unknown_motion_profile_term_errors():
    res = _run(
        "        motion_profile: ease_in_out, wiggle_fast\n"
        "        action: The char walks.\n"
    )
    assert any("wiggle_fast" in e and "motion_profile" in e for e in res.errors)
    assert not res.ok


def test_missing_motion_profile_warns_not_errors():
    res = _run("        action: The char walks calmly.\n")
    assert any("motion_profile" in w for w in res.warnings)
    # missing is warn-only; storyboard can still be ok
    assert not any("motion_profile" in e for e in res.errors)


def test_two_easings_error():
    res = _run(
        "        motion_profile: ease_in, ease_out, on_twos\n"
        "        action: The char walks.\n"
    )
    assert any("multiple easing" in e for e in res.errors)
    assert not res.ok


def test_two_cadences_error():
    res = _run(
        "        motion_profile: ease_in_out, on_ones, on_twos\n"
        "        action: The char walks.\n"
    )
    assert any("multiple cadence" in e for e in res.errors)
    assert not res.ok


def test_impact_action_without_follow_through_warns():
    res = _run(
        "        motion_profile: ease_in, on_ones\n"
        "        action: The char leaps across the gap and lands hard.\n"
    )
    assert any("follow_through" in w for w in res.warnings)


def test_impact_action_with_follow_through_no_warn():
    res = _run(
        "        motion_profile: ease_in, on_ones, follow_through\n"
        "        action: The char leaps across the gap and lands hard.\n"
    )
    assert not any("follow_through" in w for w in res.warnings)


def test_calm_action_no_follow_through_no_warn():
    res = _run(
        "        motion_profile: ease_in_out, on_twos\n"
        "        action: The char walks slowly and sits down.\n"
    )
    assert not any("follow_through" in w for w in res.warnings)
