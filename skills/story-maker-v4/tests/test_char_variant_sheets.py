"""Tests for Phase 2 character expression/pose sheet prompt builders."""

from __future__ import annotations

from tools import char_sheet_builder as csb


def _char():
    return {
        "id": "char_01",
        "name": "Kemi",
        "appearance": "A young girl with curly auburn hair and a green pinafore.",
        "species": "Human",
        "expressions": ["Mischievous grin", "Wide-eyed wonder"],
    }


def test_expression_sheet_leads_with_signature_expressions():
    p = csb.build_expression_sheet_prompt(_char(), render_style="stylized 2D anime")
    assert "EXPRESSION SHEET" in p
    assert "Kemi" in p
    # signature expressions appear, and lead the grid
    assert "Mischievous grin" in p
    assert "Wide-eyed wonder" in p
    assert p.index("Mischievous grin") < p.index("Happy")  # signature before generic
    # viseme mouth chart present
    assert "MBP (closed)" in p and "FV (teeth-lip)" in p


def test_expression_sheet_caps_at_12():
    char = _char()
    char["expressions"] = [f"Expr{i}" for i in range(20)]
    p = csb.build_expression_sheet_prompt(char, render_style="2D")
    # numbered list capped at 12
    assert "12. " in p
    assert "13. " not in p


def test_pose_sheet_uses_action_poses_and_defaults():
    p = csb.build_pose_sheet_prompt(_char(), render_style="3D cartoon")
    assert "POSE SHEET" in p
    assert "Kemi" in p
    # default poses present when none provided
    assert "Walk cycle" in p or "full-body" in p


def test_pose_sheet_respects_custom_poses():
    char = _char()
    char["action_poses"] = ["Kemi doing a cartwheel", "Kemi balancing on one foot"]
    p = csb.build_pose_sheet_prompt(char, render_style="2D")
    assert "cartwheel" in p
    assert "balancing on one foot" in p


def test_viseme_and_pose_constants():
    assert "Rest (neutral)" in csb.VISEME_ROW
    assert any("Jump" in x for x in csb.POSE_LIST)
