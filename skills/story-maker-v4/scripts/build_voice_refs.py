#!/usr/bin/env python3
"""Draft voice-reference clip builder (P4). No LLM calls, no paid API.

Generates ``<assets>/voices/<cid>.wav`` — one short clip per character whose
voice should stay locked across generations — from the character's voice_bible
sample lines, using local TTS (macOS ``say`` / ``espeak``). These are DRAFT
anchors: replace them with a recorded or cloned voice for production; H3
attaches them free as ``ref_audios`` and transfers the timbre.

  python3 scripts/build_voice_refs.py --run-dir <run> [--force]

Reads ``<run>/voice_bible.md`` + ``developed_story.md`` (character names) and
writes ``<run>/../assets/voices/<cid>.wav``. Existing clips are skipped unless
``--force``. Requires ffmpeg to convert TTS output to wav.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))

from tools import validators  # noqa: E402


def _run(cmd: list[str], timeout: int = 60) -> bool:
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout).returncode == 0
    except Exception:
        return False


def _ffmpeg_ok() -> bool:
    try:
        return subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=15).returncode == 0
    except Exception:
        return False


def _tts_to_wav(text: str, out_wav: str) -> bool:
    """Synthesize text -> wav via macOS `say` or espeak, then convert to wav."""
    if sys.platform == "darwin":
        aiff = out_wav + ".aiff"
        if _run(["say", "-o", aiff, text]):
            return _run(["ffmpeg", "-y", "-i", aiff, "-ar", "32000", "-ac", "1", out_wav])
        return False
    return _run(["espeak", "-w", out_wav, text]) or _run(["espeak-ng", "-w", out_wav, text])


def main() -> int:
    p = argparse.ArgumentParser(description="Build draft per-character voice reference clips")
    p.add_argument("--run-dir", required=True, help="episode run dir")
    p.add_argument("--force", action="store_true", help="regenerate existing clips")
    args = p.parse_args()

    run_dir = args.run_dir
    if not os.path.isdir(run_dir):
        print(f"run dir not found: {run_dir}")
        return 2
    if not _ffmpeg_ok():
        print("voice refs: ffmpeg is required but not found on PATH.")
        return 2

    bible_path = os.path.join(run_dir, "voice_bible.md")
    if not os.path.isfile(bible_path):
        print(f"voice_bible.md not found: {bible_path} — author it first (Agent 1)")
        return 2
    bible = validators.parse_voice_bible(open(bible_path, encoding="utf-8").read())
    chars = bible.get("characters", {})
    if not chars:
        print("voice_bible has no character entries")
        return 2

    # Character names from developed_story.md for a natural spoken intro
    names: dict[str, str] = {}
    story_path = os.path.join(run_dir, "developed_story.md")
    if os.path.isfile(story_path):
        story = open(story_path, encoding="utf-8").read()
        for cid, entry in chars.items():
            m = None
            if entry.get("fields", {}).get("voice_description"):
                # optional: look up "char_NN ... Name" in the characters section
                mm = __import__("re").search(
                    rf"{cid}\b[^A-Z\n]*([A-Z][a-zA-Z]+)", story)
                if mm:
                    m = mm.group(1)
            names[cid] = m or cid

    out_dir = os.path.join(os.path.dirname(os.path.abspath(run_dir)), "assets", "voices")
    os.makedirs(out_dir, exist_ok=True)

    built = 0
    for cid, entry in chars.items():
        out_wav = os.path.join(out_dir, f"{cid}.wav")
        if os.path.isfile(out_wav) and os.path.getsize(out_wav) > 0 and not args.force:
            print(f"  voice ref {cid}: exists, skip (use --force to regenerate)")
            continue
        samples = entry.get("samples", [])
        text = " ".join(samples[:2]) if samples else entry.get("fields", {}).get("voice_description", "")
        if not text:
            print(f"  voice ref {cid}: no sample lines to speak, skip")
            continue
        spoken = f"{names.get(cid, cid)}. {text}"
        if _tts_to_wav(spoken, out_wav):
            print(f"  voice ref {cid}: draft clip -> {out_wav}")
            built += 1
        else:
            print(f"  voice ref {cid}: TTS failed, skip")

    print(f"done: {built} draft voice clip(s) in {out_dir}")
    print("These are DRAFT anchors (local TTS). Replace with recorded/cloned voices")
    print("for production — H3 transfers the timbre of whatever clip is attached.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
