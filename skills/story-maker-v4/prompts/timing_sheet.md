# Timing Sheet — <scene> <gen> (exposure-sheet lite)

> Authored by Agent 3 (Storyboard Planner), one per generation
> (`timing_sheet_<scene>_g<gen>.md`). This is the X-sheet analogue: it maps the
> generation's 5–20s to **0.5s rows** of dialogue-phoneme cues, action keys,
> camera keys, and sound keys. Agent 5 compiles it into the Ref2VA prompt's
> `detailed_description` timeline. Validate:
> `python3 scripts/validate.py timing_sheet_<scene>_g<gen>.md --schema timing_sheet --run-dir <run_dir>`

duration_seconds: <this generation's duration, 5.0–20.0>

| time | dialogue | action | camera | sound |
|------|----------|--------|--------|-------|
| 0.0  | - | <key pose / action key> | <camera key> | <sound key> |
| 0.5  | <spoken words or phoneme cue, or "-> | <action key> | <camera key> | <sound key> |
| 1.0  | - | <action key> | <camera key> | <sound key> |

## Rules

- Rows ascend in time, start at 0.0, and reach the generation's end; aim for
  0.5s granularity (validator warns if rows drift past ~0.6s apart).
- **Dialogue cell** carries the spoken words (or a phoneme cue) only on the
  rows where the line is actually delivered; `-` elsewhere.
- **Lip-sync rule:** a character's line sits on rows where that character's
  mouth is on-camera. If the speaker is off-frame, mark the cell `(VO)`.
- **Dialogue fits the time:** the validator errors if a line's word count
  exceeds ~2.5 words/sec for the rows it spans. Split long lines across rows
  or extend the shot.
- **Action/camera/sound keys** are short pose-to-pose anchors, not prose.
