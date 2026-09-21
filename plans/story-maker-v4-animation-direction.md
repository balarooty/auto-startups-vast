# Story Maker V4 → Full Animation/Cartoon Direction

**Status:** Phase 1 ✅ done + tested · Phase 2 ✅ done + tested · Phase 3 ✅ done + tested · Phase 4 deferred.
**Target skill:** `skills/story-maker-v4/` (brain = Claude Code runbook, hands = deterministic Python).
**Goal:** elevate v4 from "storyboard → paid H3 render" into a real cartoon-direction
pipeline: 12-principles motion grammar, per-episode style/sound bibles, character
expression sheets, exposure-sheet-style timing, and an animatic gate that validates
pacing before any paid render.

---

## 1. Gap analysis (validated against professional practice + 2026 AI-animation consensus)

Sources consulted: Disney/Johnston-Thomas 12 principles (via Anijam's AI-adaptation
write-up), exposure-sheet/X-sheet layout (Wikipedia), storyboard-vs-animatic timing
argument (Ciaro Pro), AI storyboard→animation pipeline (Neolemon), and the 2026
Kling/Seedance/Veo anime comparison (Elser AI).

v4 already has: anticipation→action→reaction→settle acting beats, squash & stretch,
spatial plan + QA, 235-question critique, H3 style LoRAs, per-shot 4-layer audio.

Genuine gaps:

| # | Gap | Why it matters (research) |
|---|-----|---------------------------|
| G1 | **No animatic / timing-validation stage** — stills go straight to paid 20s renders | Storyboards validate structure; animatics validate pacing. Skipping this is the #1 cited source of wasted AI render credits. |
| G2 | **12 principles only partially formalized** — no easing (slow in/out) on camera moves, no on-ones/twos cadence, follow-through/secondary action advisory not enforced | Exactly the principles AI video models skip (follow-through, slow in/out, solid drawing), producing "stiff puppet" motion. |
| G3 | **No exposure-sheet artifact** — timing is second-granularity only; no phoneme-level dialogue cues for lip-sync | Classic X-sheets map dialogue phonemes + action keys to frames; H3 lip-syncs visible faces, so dialogue length vs shot length and on/off-camera mouth must be planned. |
| G4 | **Character sheets are identity-only** — no expression sheet / pose sheet / mouth chart | Identified as the core fix for shot-to-shot face drift and lifeless acting. |
| G5 | **Style is a free-text line per scene** — no per-episode art-direction bible | Without a palette/shape/line lock, scenes drift visually across 20s generations. |
| G6 | **Sound is per-shot** — no leitmotif/score map | Each generation invents its own music; no cross-scene musical continuity. |
| G7 | **Backend locked to MiniMax H3** | 2026 consensus: no single model wins (Kling 3.0 = directed action, Seedance 2.0 = multi-reference, Veo 3.1 = cinematic polish). Deferred to Phase 4. |

---

## 2. Phase 1 — Authoring-layer craft (no render changes; highest ROI)

### 2.1 Extend the cinematography bible to the full 12 principles
**File:** `skills/story-maker-v4/assets/cinematography-bible.md`

Expand Section G (currently micro-beat mechanics + squash & stretch + follow-through
prose) into a complete **12 Principles of Animation for AI Video** section. Each
principle gets: one-line definition, why AI models fail at it, and **concrete prompt
phrasing** usable in `action:` / `camera:` fields:

1. Squash & stretch (already present — keep, tighten)
2. Anticipation (already present)
3. Staging (link to Section H composition)
4. Straight-ahead vs pose-to-pose → map to "key pose naming" in `action:`
5. Follow-through & overlapping action (exists as prose; make a required phrasing pattern)
6. **Slow in / slow out → NEW: easing vocabulary** (`ease_in`, `ease_out`, `ease_in_out`, `linear`, `snap`) applied to camera moves and character motion
7. Arcs (natural movement arcs vs straight lines)
8. Secondary action (cloth/hair/ears — exists as Q6.5; promote to field guidance)
9. **Timing → NEW: cadence vocabulary** (`on_ones` 24/25fps full, `on_twos` 12fps anime hold, `hold` poses) — the single biggest "cartoon feel" lever
10. Exaggeration (exists as Q6.7)
11. Solid drawing / model consistency (link to character sheets + spatial plan)
12. Appeal (silhouette + readability, links to `layout_strategy`)

### 2.2 New per-shot `motion_profile:` field
**Files:** `skills/story-maker-v4/prompts/storyboard_planner.md`,
`skills/story-maker-v4/tools/validators.py`

Add an optional-but-encouraged shot field:
```
motion_profile: ease_in_out, on_twos, follow_through
```
- Grammar: comma list drawn from a new `MOTION_PROFILE_TERMS` tuple in `validators.py`
  (`ease_in`, `ease_out`, `ease_in_out`, `linear`, `snap`, `on_ones`, `on_twos`,
  `hold`, `follow_through`, `overlapping`, `secondary_motion`).
- Validator: unknown term → `error`; missing field → `warn` (mirrors the existing
  `shot_size`/`composition` "encouraged" pattern at `validators.py` ~695–708).
- Cross-check: a shot whose `action:` contains an impact/leap verb but whose
  `motion_profile` lacks `follow_through` → `warn` (add to the storyboard shot loop).
- Update the Field-notes block and worked example in `storyboard_planner.md`.

### 2.3 Animation-craft critique questions
**Files:** `skills/story-maker-v4/assets/directing-questions.md`,
`skills/story-maker-v4/prompts/critique_agent.md`

Append ~40 questions to **Section 6: Animation Direction** (currently 25, Q6.1–Q6.25):
- Q6.26+: easing on every camera move; on-twos cadence for 2D targets; follow-through
  present on every impact; secondary action on every major move; pose-to-pose key poses
  named; dialogue length fits the shot (word-count vs seconds); mouth on-camera when
  speaking; hold poses at shot ends for clean generation handoff. Cross-reference the
  existing Q6.21/Q6.22 climax/quiet questions rather than duplicating them.
- Update the header count "(25 questions)" and the critique agent's section map in
  `prompts/critique_agent.md`.

---
## 3. Phase 2 — New artifacts

### 3.1 `style_bible.md` (per-episode art-direction lock) — Agent 1
**Files:** new `skills/story-maker-v4/prompts/style_bible.md` template,
`prompts/story_developer.md`, `tools/validators.py`, `scripts/validate.py`

- Agent 1 (Story Developer) authors `<run_dir>/style_bible.md` alongside
  `developed_story.md`: production target, **palette script** (emotional color arc
  scene-by-scene), line weight / shape language, background treatment, texture/grain,
  lighting rules, and an explicit do/don't list. No studio/brand names (existing rule).
- New validator schema `style_bible` (add to the `choices` tuple in
  `scripts/validate.py`): requires the locked sections; palette must name one entry
  per scene id.
- Extend the `scenes` validator: when `style_bible.md` is present in the run dir,
  cross-check each scene's `style_target`/`visual_motif` against the bible's do/don't
  and palette (warn on contradiction).

### 3.2 Character expression & pose sheets — performance assets
**Files:** `skills/story-maker-v4/tools/char_sheet_builder.py`,
`prompts/character_sheet_template.md`, `skills/story-maker-v4/scripts/build_images.py`,
`prompts/image_prompter.md`, `prompts/story_developer.md`

- `char_sheet_builder.py` already defines `EXPRESSION_LIST` (12 expressions) and
  `TURNAROUND_VIEWS` (8 views) — currently used only inside the single identity sheet.
  Emit **two additional sheets per character**:
  - `char_NN_expressions.webp` — 12-expression grid (reuse `EXPRESSION_LIST`) + a
    viseme/mouth row (AI/E/O/U/MBP/FV/L/rest).
  - `char_NN_poses.webp` — key action poses (idle, walk, run, jump, sit, reach).
- `build_images.py::build_assets` (line ~65): add these two asset kinds to the
  per-character loop, register them in `asset_registry.json`, and make them resume-safe
  like existing assets.
- Asset registry gains stable ids `char_NN_expressions`, `char_NN_poses` so later
  episodes reuse them (no regen).
- Agent 1 adds an `## Expressions` subsection per character in `developed_story.md`
  (the 3–4 signature expressions for that character's personality).
- Agent 4 (`image_prompter.md`) attaches the expression sheet as an extra reference
  for acting-heavy storyboard sheets.

### 3.3 `sound_map.md` (score/leitmotif plan) — Agent 2
**Files:** new `skills/story-maker-v4/prompts/sound_map.md` template,
`prompts/scene_writer.md`, `prompts/video_prompter.md`, `tools/validators.py`

- Agent 2 authors `<run_dir>/sound_map.md` with scenes.md: per-scene ambience bed,
  **character leitmotifs**, sting/reveal moments, and the episode music arc
  (intro → build → climax → button).
- New validator schema `sound_map`; cross-check every scene id in `scenes.md` has an
  entry and every named character has a motif.
- Agent 5's `non_diegetic_music` layer (the 4-layer audio block in
  `video_prompter.md`) then **references motif names** instead of inventing per-shot
  music — giving continuity across 20s generations. Update `video_prompter.md` to
  require motif references.

### 3.4 Per-generation timing sheet (exposure-sheet lite) — Agent 3
**Files:** new `skills/story-maker-v4/prompts/timing_sheet.md` template,
`prompts/storyboard_planner.md`, `prompts/video_prompter.md`, `tools/validators.py`

- Agent 3 authors `<run_dir>/timing_sheet_<scene>_g<gen>.md` per generation: rows at
  **0.5s granularity** with columns `time | dialogue_phoneme_cue | action_key |
  camera_key | sound_key`. This is the X-sheet analogue — phoneme cues for lip-sync,
  action keys for pose-to-pose, camera keys for moves.
- New validator schema `timing_sheet`: rows contiguous, cover the generation's
  5–20s, and **dialogue word-count vs duration check** (≈2.5 words/sec ceiling →
  error if a line can't fit its shot).
- Agent 5 compiles the timing sheet into the Ref2VA prompt's `detailed_description`
  timeline; add lip-sync rule: speaker's mouth must be on-camera during their `<d>`
  line, else mark the line off-screen (VO).

---

## 4. Phase 3 — Animatic stage + GATE 1.5

### 4.1 `scripts/build_animatic.py` (new, deterministic, no LLM)
**Files:** new `skills/story-maker-v4/scripts/build_animatic.py`,
`skills/story-maker-v4/SKILL.md`, possibly `tools/video_frames.py`

- Input: a scene's rendered storyboard sheets + `storyboard_<scene>.md` shot timing.
- Slice each sheet into its panels (`panel_grid`, column-major) via
  `tools/video_frames.py` helpers or PIL; assemble a slideshow where each shot holds
  for its exact duration; add a **scratch audio** track (macOS `say` / espeak TTS for
  dialogue lines, or a silent temp tone) via `ffmpeg`.
- Output: `<run_dir>/animatic_<scene>.mp4`, plus a stitched
  `<run_dir>/animatic_full.mp4` using the existing `tools/video_concat.py`.
- Reuses existing ffmpeg concat; adds only PIL slicing + TTS. No paid calls.

### 4.2 GATE 1.5 in the runbook
**File:** `skills/story-maker-v4/SKILL.md`

Insert between Stage B (GATE 1, sheets) and Stage C (video prompts / GATE 2):

```
═══ GATE 1 ═══ (sheets + spatial_qa)
   → build_animatic.py per scene
═══ GATE 1.5 ═══ user confirms PACING/TIMING on animatic_<scene>.mp4
   → Stage C (video prompts)
═══ GATE 2 ═══ (render manifest, paid render)
```

Update: the pipeline diagram (~lines 120–132), the stage list (~151–161), add a
"Stage B.5 — Animatic" section, and add pitfall #14: "Never render paid video before
the animatic passes — pacing errors are cheapest to fix at the animatic, costliest at
the render."

---

## 5. Validation & testing

- Extend `skills/story-maker-v4/tests/` with new cases:
  - `test_motion_profile.py` — term whitelist, missing-field warn, follow-through warn.
  - `test_style_bible.py` / `test_sound_map.py` / `test_timing_sheet.py` — schema +
    cross-checks (dialogue word-count vs duration).
  - Animatic: unit-test panel slicing math on a synthetic sheet; smoke-test
    `build_animatic.py` on a tiny fixture (no network).
- Run `python3 -m pytest skills/story-maker-v4/tests/` and the existing
  `validate.py` suite to confirm no regressions to current schemas.

---

## 6. Phase 4 (deferred — record only)

Model-agnostic render backend + per-generation routing: abstract
`tools/minimax_workflow.py` behind a backend interface; tag generations
(dialogue-heavy → H3 native audio, action choreography → Kling 3.0, establishing →
Veo 3.1). Keep H3 the default. Not in the approved scope.

---

## 7. File-touch summary

| File | Change |
|------|--------|
| `assets/cinematography-bible.md` | expand §G → full 12 principles + prompt phrasing |
| `assets/directing-questions.md` | +40 animation-craft questions (Section 6) |
| `prompts/storyboard_planner.md` | add `motion_profile:` + timing-sheet output |
| `prompts/story_developer.md` | + style_bible + character `## Expressions` |
| `prompts/scene_writer.md` | + sound_map output |
| `prompts/video_prompter.md` | motif references + lip-sync rule + timing-sheet compile |
| `prompts/critique_agent.md` | wire new Section-6 questions |
| `prompts/image_prompter.md` | attach expression sheets as references |
| `prompts/character_sheet_template.md` | expression/pose grid templates |
| new `prompts/style_bible.md`, `prompts/sound_map.md`, `prompts/timing_sheet.md` | templates |
| `tools/validators.py` | `MOTION_PROFILE_TERMS` + 3 new schemas + cross-checks |
| `scripts/validate.py` | add `style_bible`/`sound_map`/`timing_sheet` to choices |
| `tools/char_sheet_builder.py` | emit expression + pose sheets |
| `scripts/build_images.py` | build new asset kinds, registry entries |
| new `scripts/build_animatic.py` | animatic builder |
| `SKILL.md` | GATE 1.5 + Stage B.5 + pitfall #14 |
| `tests/` | new test modules |

