#!/usr/bin/env python3
"""Animatic builder (the "hands"). No LLM calls, no paid image/video calls.

Slices each scene's rendered storyboard sheets into per-shot panels and
assembles a duration-timed slideshow — the *animatic* — so the director can
validate pacing and cut rhythm BEFORE any paid Minimax H3 render (GATE 1.5).

  python3 scripts/build_animatic.py --output-dir <run> --scene s1
      # one scene: animatic_s1.mp4 (panel slideshow + scratch audio)

  python3 scripts/build_animatic.py --output-dir <run> --all
      # every scene + a stitched animatic_full.mp4

A shot holds its first panel for the shot's exact duration (scene-relative
start/end from storyboard_<scene>.md). Scratch audio: spoken dialogue via TTS
(macOS `say` / `espeak`) or a silent temp track otherwise. Sheets are sliced
by their declared `panel_grid` (default 3x2), column-major numbering — the same
topology the storyboard validator enforces.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))

from tools import validators  # noqa: E402
from tools import video_concat  # noqa: E402

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


def _run(cmd: list[str], timeout: int = 120) -> bool:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            print(f"  animatic cmd failed ({cmd[0]}): {r.stderr[-200:]}", file=sys.stderr)
        return r.returncode == 0
    except FileNotFoundError:
        print(f"  animatic: executable not found: {cmd[0]}", file=sys.stderr)
        return False
    except Exception as e:  # pragma: no cover
        print(f"  animatic cmd error ({cmd[0]}): {e}", file=sys.stderr)
        return False


def _ffmpeg_available() -> bool:
    try:
        return subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, timeout=15
        ).returncode == 0
    except Exception:
        return False


def _parse_grid(grid: str) -> tuple[int, int]:
    """'3x2' (3 rows x 2 columns) -> (rows, cols). Default 3x2."""
    m = re.match(r"^\s*(\d+)\s*x\s*(\d+)\s*$", grid or "")
    if not m:
        return (3, 2)
    return (int(m.group(1)), int(m.group(2)))


def slice_sheet(sheet_path: str, grid: str, out_dir: str) -> list[str]:
    """Slice a storyboard sheet into panels, column-major numbering.

    Panel 1 is top-left; numbering runs top-to-bottom within a column, then
    left-to-right across columns (matches the storyboard validator's topology).
    Returns panel paths ordered by panel number (index 0 = panel 1).
    """
    if Image is None:
        raise RuntimeError("Pillow is required: pip install pillow")
    rows, cols = _parse_grid(grid)
    os.makedirs(out_dir, exist_ok=True)
    with Image.open(sheet_path) as im:
        w, h = im.size
        pw, ph = w // cols, h // rows
        panels: list[str] = [""] * (rows * cols)
        for col in range(cols):
            for row in range(rows):
                idx = col * rows + row  # panel number - 1 (column-major)
                box = (col * pw, row * ph, (col + 1) * pw, (row + 1) * ph)
                out = os.path.join(out_dir, f"panel_{idx + 1:02d}.png")
                im.crop(box).save(out)
                panels[idx] = out
    return panels


def _tts(text: str, out_wav: str) -> bool:
    """Synthesize a line to a wav via macOS `say` or `espeak`."""
    if sys.platform == "darwin":
        aiff = out_wav + ".aiff"
        if _run(["say", "-o", aiff, text]):
            return _run(["ffmpeg", "-y", "-i", aiff, out_wav])
        return False
    return _run(["espeak", "-w", out_wav, text]) or _run(["espeak-ng", "-w", out_wav, text])


def _silence(seconds: float, out_wav: str) -> bool:
    return _run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
        "-t", f"{max(seconds, 0.1):.2f}", out_wav,
    ])


def _extract_dialogue(dialogue_field: str) -> list[str]:
    """`char_01: "line", char_02: "line2"` -> ['line', 'line2']."""
    return re.findall(r'"([^"]+)"', dialogue_field or "")

def build_scene_animatic(run_dir: str, scene_id: str, *, scratch_audio: bool = True) -> str:
    """Build animatic_<scene>.mp4. Returns the output path."""
    sb = validators.parse_storyboard(
        open(os.path.join(run_dir, f"storyboard_{scene_id}.md"), encoding="utf-8").read()
    )
    segments: list[str] = []
    tmp = tempfile.mkdtemp(prefix=f"animatic_{scene_id}_")
    seg_idx = 0

    for gen in sb.get("generations", []):
        if gen.get("is_bridge"):
            continue
        gid = gen["gen_id"]
        grid = gen.get("panel_grid") or "3x2"
        sheet = os.path.join(run_dir, f"storyboard_sheet_{scene_id}_{gid}.webp")
        if not os.path.isfile(sheet):
            sheet = os.path.join(run_dir, f"storyboard_sheet_{scene_id}_{gid}.png")
        if not os.path.isfile(sheet):
            raise SystemExit(f"animatic: storyboard sheet not found for {scene_id}/{gid}")
        panels = slice_sheet(sheet, grid, os.path.join(tmp, f"{gid}_panels"))

        for shot in gen.get("shots", []):
            start, end = shot.get("start"), shot.get("end")
            if start is None or end is None:
                continue
            dur = max(end - start, 0.2)
            pnums = [p for p in shot.get("panels", []) if isinstance(p, int) and p >= 1]
            panel = panels[pnums[0] - 1] if pnums and pnums[0] - 1 < len(panels) else panels[0]

            wav = os.path.join(tmp, f"seg{seg_idx:03d}.wav")
            lines = _extract_dialogue(shot.get("dialogue", "")) if scratch_audio else []
            if lines and not _tts(" ".join(lines), wav):
                _silence(dur, wav)
            elif not lines:
                _silence(dur, wav)

            seg = os.path.join(tmp, f"seg{seg_idx:03d}.mp4")
            ok = _run([
                "ffmpeg", "-y",
                "-loop", "1", "-t", f"{dur:.2f}", "-i", panel,
                "-i", wav,
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest",
                seg,
            ], timeout=180)
            if ok and os.path.isfile(seg):
                segments.append(seg)
                seg_idx += 1

    if not segments:
        raise SystemExit(f"animatic: no segments produced for {scene_id}")

    out_path = os.path.join(run_dir, f"animatic_{scene_id}.mp4")
    result = video_concat.concat_videos(segments, out_path)
    if result.get("status") != "success":
        raise SystemExit(f"animatic concat failed for {scene_id}: {result.get('message')}")
    print(f"  animatic {scene_id}: {len(segments)} shots -> {out_path}")
    return out_path


def main() -> int:
    p = argparse.ArgumentParser(description="Build animatic(s) from storyboard sheets")
    p.add_argument("--output-dir", required=True, help="run output dir")
    p.add_argument("--scene", default=None, help="scene id (e.g. s1)")
    p.add_argument("--all", action="store_true", help="all scenes + stitched animatic_full.mp4")
    p.add_argument("--no-audio", action="store_true", help="skip TTS; silent temp track")
    args = p.parse_args()

    run_dir = args.output_dir
    if not os.path.isdir(run_dir):
        print(f"run dir not found: {run_dir}")
        return 2
    if not _ffmpeg_available():
        print("animatic: ffmpeg is required but not found on PATH. "
              "Install ffmpeg (an existing pipeline dependency) and retry.")
        return 2

    scene_ids: list[str] = []
    if args.all:
        scenes = validators.parse_scenes(
            open(os.path.join(run_dir, "scenes.md"), encoding="utf-8").read()
        )
        scene_ids = [sc["scene_id"] for sc in scenes.get("scenes", [])]
    elif args.scene:
        scene_ids = [args.scene]
    else:
        print("pass --scene <id> or --all")
        return 2

    built = [
        build_scene_animatic(run_dir, sid, scratch_audio=not args.no_audio)
        for sid in scene_ids
    ]

    if args.all and len(built) > 1:
        full = os.path.join(run_dir, "animatic_full.mp4")
        result = video_concat.concat_videos(built, full)
        if result.get("status") == "success":
            print(f"  animatic full: {full}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

