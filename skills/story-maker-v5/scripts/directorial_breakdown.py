#!/usr/bin/env python3
"""Assemble a human-readable directorial breakdown for a run.

    python3 scripts/directorial_breakdown.py --run-dir <run>
    python3 scripts/directorial_breakdown.py --run-dir <run> --out report.md

Deterministic — no model calls. Reuses the same parsers the validators use
(tools/validators.py), so the document can never drift from what passed
validation. Emits ``<run_dir>/directorial_breakdown.md``:

  Logline & Directorial Intent   <- developed_story.md ## Directorial Intent
  Narrative Arc                  <- beat_board.md beats
  Color Script                   <- developed_story.md ## Color Script +
                                    per-scene color_script
  Character & Asset Manifest     <- story.json (+ per-character state_changes)
  Constraints                    <- story.json constraints
  Shot-by-Shot                   <- storyboard_<scene>.md (timecode, transition,
                                    framing, camera, action, dialogue, audio stems)

Run it before the render gate — it is the review document a human reads
before spending render money, in the style of a director's analysis.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))

from tools import validators  # noqa: E402


def _read(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def _md_section(md: str, name: str) -> str:
    """Extract the body of a ``## <name>`` section (up to the next ``## ``)."""
    m = re.search(
        r"^##\s+" + re.escape(name) + r"\s*$\n(.*?)(?=^##\s|\Z)",
        md, flags=re.M | re.S,
    )
    return m.group(1).strip() if m else ""


def _fmt_range(shot: dict) -> str:
    s, e = shot.get("start"), shot.get("end")
    if s is None or e is None:
        return "?"
    return f"{s:05.1f}-{e:05.1f}"


def _shot_audio_lines(shot: dict) -> str:
    """One audio summary per shot: stems preferred, flat audio fallback."""
    stems = [
        ("Dia", shot.get("audio_dia", "")),
        ("FX", shot.get("audio_fx", "")),
        ("Amb", shot.get("audio_amb", "")),
        ("Mus", shot.get("audio_mus", "")),
    ]
    parts = [f"{label}: {val}" for label, val in stems if val]
    if parts:
        return " / ".join(parts)
    return shot.get("audio", "") or "-"


def build_breakdown(run_dir: str) -> str:
    story: dict = {}
    sj = os.path.join(run_dir, "story.json")
    if os.path.isfile(sj):
        story = json.loads(_read(sj))
    dev = _read(os.path.join(run_dir, "developed_story.md"))
    beats_md = _read(os.path.join(run_dir, "beat_board.md"))
    scenes_md = _read(os.path.join(run_dir, "scenes.md"))

    storyboards: list[tuple[str, dict]] = []
    for name in sorted(os.listdir(run_dir)):
        if name.startswith("storyboard_") and name.endswith(".md"):
            sb = validators.parse_storyboard(_read(os.path.join(run_dir, name)))
            storyboards.append((name, sb))

    title = story.get("title") or os.path.basename(run_dir.rstrip("/"))
    out: list[str] = [
        f"# Directorial Breakdown — {title}",
        "",
        "Assembled from the run's planning artifacts — the review document "
        "to read before the render gate.",
        "",
    ]

    intent = _md_section(dev, "Directorial Intent")
    out.append("## Logline & Directorial Intent")
    out.append("")
    out.append(intent or "_(no `## Directorial Intent` section in developed_story.md)_")
    out.append("")

    if beats_md:
        bb = validators.parse_beat_board(beats_md)
        if bb["beats"]:
            out += [
                "## Narrative Arc",
                "",
                "| beat | emotion | est. seconds | description |",
                "|---|---|---|---|",
            ]
            for b in bb["beats"]:
                out.append(
                    f"| {b['beat_num']} | {b['emotion'] or '-'} | "
                    f"{b['estimated_seconds']}s | {b['description']} |"
                )
            out.append("")

    color_section = _md_section(dev, "Color Script")
    scenes = validators.parse_scenes(scenes_md)["scenes"] if scenes_md else []
    scene_colors = {s["scene_id"]: s["color_script"] for s in scenes if s.get("color_script")}
    if color_section or scene_colors:
        out.append("## Color Script")
        out.append("")
        if color_section:
            out.append(color_section)
            out.append("")
        if scene_colors:
            out += ["| scene | palette |", "|---|---|"]
            for sid, cs in scene_colors.items():
                out.append(f"| {sid} | {cs} |")
            out.append("")

    chars = story.get("characters", [])
    locs = story.get("locations", [])
    objs = story.get("objects", [])
    if chars or locs or objs:
        out.append("## Character & Asset Manifest")
        out.append("")
        if chars:
            out += ["| id | name | state changes |", "|---|---|---|"]
            for c in chars:
                changes = c.get("state_changes") or []
                rendered = " → ".join(
                    f"{ch.get('becomes', '?')} (@{ch.get('at', '?')})"
                    for ch in changes
                )
                out.append(f"| {c.get('id','')} | {c.get('name','')} | {rendered or '-'} |")
            out.append("")
        if locs:
            out += ["| id | location |", "|---|---|"]
            for l in locs:
                out.append(f"| {l.get('id','')} | {l.get('name','')} |")
            out.append("")
        if objs:
            out += ["| id | object | states |", "|---|---|---|"]
            for o in objs:
                out.append(
                    f"| {o.get('id','')} | {o.get('name','')} | "
                    f"{', '.join(o.get('states', [])) or '-'} |"
                )
            out.append("")

    constraints = story.get("constraints", [])
    if constraints:
        out += ["## Constraints", "", "| id | type | severity | rule |", "|---|---|---|---|"]
        for c in constraints:
            out.append(
                f"| {c.get('id','')} | {c.get('type','')} | "
                f"{c.get('severity','')} | {c.get('rule','')} |"
            )
        out.append("")

    if storyboards:
        out.append("## Shot-by-Shot")
        out.append("")
        for name, sb in storyboards:
            sid = sb["scene_id"] or name
            sc_meta = next((s for s in scenes if s["scene_id"] == sid), None)
            out.append(f"### Scene {sid} — {sb.get('title','')}")
            out.append("")
            if sc_meta and sc_meta.get("color_script"):
                out.append(f"palette: {sc_meta['color_script']}")
                out.append("")
            out += [
                "| shot | range | transition | size | angle | action | dialogue | audio |",
                "|---|---|---|---|---|---|---|---|",
            ]
            for gen in sb["generations"]:
                if gen.get("is_bridge"):
                    continue
                for shot in gen["shots"]:
                    states = shot.get("char_state") or {}
                    action = shot.get("action", "")
                    if states:
                        action += " [" + "; ".join(
                            f"{k}={v}" for k, v in states.items()
                        ) + "]"
                    out.append(
                        f"| {gen['gen_id']}/s{shot['shot']} | "
                        f"{_fmt_range(shot)}s | {shot.get('transition','')} | "
                        f"{shot.get('shot_size','-') or '-'} | "
                        f"{shot.get('camera_angle','-') or '-'} | "
                        f"{action} | {shot.get('dialogue','') or '-'} | "
                        f"{_shot_audio_lines(shot)} |"
                    )
            out.append("")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Emit directorial_breakdown.md for a run")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--out", default="", help="output path (default <run_dir>/directorial_breakdown.md)")
    args = p.parse_args()
    run_dir = os.path.abspath(args.run_dir)
    out_path = args.out or os.path.join(run_dir, "directorial_breakdown.md")
    text = build_breakdown(run_dir)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
