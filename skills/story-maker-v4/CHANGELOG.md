# Changelog — Story Maker V4

All notable changes to `story-maker-v4` (and its evolutionary context from `story-maker-v3` and `story-maker-v4p`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [4.5.0] - 2026-09-19

Dialogue production fix — plan: [`plans/story-maker-v4-dialogue-fix.md`](../../plans/story-maker-v4-dialogue-fix.md).
Research basis: MiniMax H3 native-audio guidance (voice-reference clips, mumble
fixes, dialogue-forward mix ranking) + animation dialogue craft from Pixar/Disney
writers (scene intent, subtext, economy, the cover-up-names test).

### Highlights
- **P1 — dialogue lint (deterministic).** The `video_prompt` validator now errors
  on empty/placeholder `<d>` tags (silence must be directed, not spoken as "…"),
  bracketed vocalizations inside `<d>` (`[Gasp!]` would be spoken as the word
  "gasp"), duplicate lines within a generation, and lines exceeding ~2.5 words/sec
  for their shot. Warns on cross-cut line repetition (anti-repetition gate) and
  missing dialogue-forward mix ranking.
- **P2 — Voice Bible** (`voice_bible.md` + `--schema voice_bible`): per-character
  H3 voice description, speech patterns, signature vocabulary, taboos, sample
  lines, and relationship registers. Coverage against the scene cast is checked,
  sample lines are linted, and near-identical speech patterns warn (the
  cover-up-names test). Authored by Agent 1; Agents 2/3/5 must match it.
- **P3 — dedicated dialogue pass (Agent 1c):** a rewrite-for-voice step between
  the beat board and scenes (`prompts/dialogue_pass.md`): scene intent, subtext,
  voice lock, economy, cover-up-names, anti-repetition; screenplay re-validated
  after.
- **P5 — dialogue-forward mix ranking** documented in the 4-layer audio block.
- **P4 — voice timbre anchoring:** `render_all.py` attaches
  `<story>/assets/voices/<cid>.wav` clips as H3 `ref_audios` for speaking
  characters (billed free by H3); new `scripts/build_voice_refs.py` builds draft
  clips from the voice bible via local TTS; `VOICE_REFS_ENABLED` flag.
- **Golden example:** `assets/dialogue-golden-example.md` — real before/after
  fixes for empty tags, spoken vocalizations, and duplicate lines.

### Added
- `lint_dialogue_tag()` + `validate_voice_bible()` in `tools/validators.py`;
  `voice_bible` schema in `scripts/validate.py`.
- `prompts/voice_bible.md`, `prompts/dialogue_pass.md`.
- `_find_voice_refs()` in `scripts/render_all.py`; `scripts/build_voice_refs.py`;
  `VOICE_REFS_ENABLED` in `config.py`.
- `assets/dialogue-golden-example.md`.
- Tests: `tests/test_dialogue_lint.py` (11), `tests/test_voice_bible.py` (7),
  `tests/test_voice_refs.py` (4).

### Changed
- `prompts/video_prompter.md` — voice bible input, mix-ranking rule, golden
  dialogue example reference.
- `prompts/story_developer.md` — voice bible authoring.
- `prompts/scene_writer.md`, `prompts/storyboard_planner.md` — dialogue voice lock.
- `SKILL.md` — Stage A1c dialogue pass step; Stage D1 voice anchoring; version 4.5.0.
- `assets/directing-questions.md` — Q10.17 (cover-up-names test).

---

## [4.4.0] - 2026-09-19

Video-prompt quality upgrade — fixes the "prompts pass but produce mediocre video"
gap. Plan: [`plans/story-maker-v4-video-prompt-quality.md`](../../plans/story-maker-v4-video-prompt-quality.md).
Research basis: MiniMax's official H3 handbook (three-part formula; camera
decomposition; detailed prohibitions) + a cross-model study of AI video prompt
mistakes (don't re-describe references; one motion path; no generic quality words).

### Highlights
- **P1 — quality enforcement in the video_prompt validator.** The Director's Brief
  path now enforces, not just advises: panel-number references and flat audio are
  errors; identity anchors over 120 words are errors (warn >60); compound camera
  moves, untranslated `motion_profile`, thin per-second density, and style_bible
  contradictions are caught. Corpus sweep of 126 real prompts found ~500 P1 issues.
- **P2 — template rewritten to MiniMax's official 3-part formula** in
  `prompts/video_prompter.md` and `assets/minimax-h3-prompt-bible.md`: reference
  material description + core creative concept + per-second visual process.
  Identity-anchoring policy (the reference image carries identity), single camera
  motion path, detailed guardrails, timing-sheet compilation, style_bible lock.
  Fixed a stale "15.0 seconds" hardcode (generations are 5–20s).
- **P3 — craft gate.** New Section 10 (Video Prompt Quality, 16 questions) in
  `assets/directing-questions.md`, run as an Agent 5b review over
  `video_prompts/*.txt` during Stage C-Lock, before the paid render manifest locks.
- **P4 — golden example.** `assets/video-prompt-golden-example.md` rewrites a real
  weak prompt (crunchools s1_g1) to the new standard; the rewrite passes the
  updated validator with zero errors/warnings against the real storyboard.

### Added
- `tools/validators.py` — `_VIDEO_AUDIO_LAYERS`, `_PANEL_REF_RE`,
  `_CAMERA_MOTION_KEYWORDS`, `_MOTION_PROFILE_PHRASES`, `_ANIMATION/PHOTOREAL_STYLE_WORDS`;
  P1 checks in `validate_video_prompt_brief` (panel refs, 4-layer audio, identity
  budget, camera motion path, style_bible consistency, per-second density,
  motion_profile translation); `run_dir` plumbed through `validate_video_prompt`.
- `assets/directing-questions.md` Section 10 (16 questions).
- `assets/video-prompt-golden-example.md`.
- `tests/test_video_prompt_quality.py` (10 tests).

### Changed
- `prompts/video_prompter.md` — 3-part formula, identity anchoring, camera rule,
  per-second process, guardrails, style lock, motion_profile translation; golden
  example referenced; stale 15.0s hardcode fixed.
- `assets/minimax-h3-prompt-bible.md` — new §0 (official formula + hard-won rules);
  template updated to identity anchors, guardrails, 4-layer audio.
- `prompts/critique_agent.md` — question bank now 275+ across 10 sections.
- `SKILL.md` — Stage C1 rewritten for the Director's Brief + C-Lock Agent 5b craft
  review step; version 4.4.0.
- `tests/test_phase2.py` — Director's Brief fixtures updated to the 4-layer audio
  contract.

### Breaking
- The `video_prompt` validator now **errors** on flat (non-4-layer) audio blocks
  and panel-number references. Prompts authored before 4.4.0 will fail
  re-validation until updated — this is intentional (the 4-layer contract was
  already documented in `prompts/video_prompter.md`). Existing approved renders
  are unaffected; re-renders should re-author prompts to the new standard.

---

## [4.3.0] - 2026-09-19

Full animation/cartoon direction upgrade — Phases 1–3 of
[`plans/story-maker-v4-animation-direction.md`](../../plans/story-maker-v4-animation-direction.md).

### Highlights
- **12 Principles formalized** (Phase 1): cinematography bible Section G-bis maps every
  principle to "how AI fails it" + exact prompt phrasing; new per-shot `motion_profile:`
  field (easing / cadence / principle flags) enforced by the storyboard validator.
- **Animatic stage + GATE 1.5** (Phase 3): `scripts/build_animatic.py` builds a
  duration-timed panel slideshow with scratch audio from rendered sheets — pacing is
  confirmed on video **before any paid render**. Four gates now (0, 1, 1.5, 2).
- **Performance assets** (Phase 2): per-character expression sheets (12-expression grid +
  viseme mouth chart) and pose sheets generated from the identity sheet, registered for
  cross-episode reuse.
- **Art-direction lock** (Phase 2): `style_bible.md` with palette script + Do/Don't list;
  scenes validator cross-checks `style_target`/`visual_motif` against it.
- **Score continuity** (Phase 2): `sound_map.md` defines the music arc + character
  leitmotifs; Agent 5 references motifs instead of inventing per-shot music.
- **Exposure-sheet lite** (Phase 2): per-generation `timing_sheet_<scene>_g<gen>.md`
  (0.5s rows of dialogue/action/camera/sound keys); validator errors when a dialogue
  line exceeds ~2.5 words/sec (lip-sync feasibility).

### Added
- `assets/cinematography-bible.md` Section G-bis — 12 principles for AI video.
- `MOTION_PROFILE_TERMS` + follow-through heuristic in `tools/validators.py`.
- `validate_style_bible()` / `validate_sound_map()` / `validate_timing_sheet()` +
  `--schema style_bible|sound_map|timing_sheet` in `scripts/validate.py`.
- `prompts/style_bible.md`, `prompts/sound_map.md`, `prompts/timing_sheet.md`.
- `build_expression_sheet_prompt()` / `build_pose_sheet_prompt()` in
  `tools/char_sheet_builder.py`; `generate_character_variant_sheet()` +
  `AssetRegistry.character_variant_path()` in `tools/image_pipeline.py`;
  `BUILD_CHARACTER_VARIANT_SHEETS` in `config.py`.
- `scripts/build_animatic.py` — deterministic animatic builder (PIL slicing, ffmpeg,
  macOS `say`/`espeak` scratch TTS; no LLM calls, no paid calls).
- 40 new animation-craft questions (Q6.26–Q6.45; Section 6 now 45 questions).
- Tests: `tests/test_motion_profile.py` (9), `tests/test_phase2_schemas.py` (10),
  `tests/test_char_variant_sheets.py` (5), `tests/test_animatic.py` (6).

### Changed
- `prompts/storyboard_planner.md` — `motion_profile:` field docs + timing-sheet output.
- `prompts/story_developer.md` — style_bible + character signature expressions.
- `prompts/scene_writer.md` — sound_map output.
- `prompts/video_prompter.md` — motif continuity, lip-sync/VO rule, timing-sheet compile,
  motion_profile translation.
- `prompts/image_prompter.md` — expression/pose sheet references for acting shots.
- `prompts/critique_agent.md` — question-bank count updated (260+).
- `SKILL.md` — GATE 1.5 + Stage B.5 + pitfalls #9/#14 updated; version 4.3.0.
- `ARCHITECTURE.md` — pipeline diagrams, gate summary, and file map updated.

---

## [4.2.0] - 2026-09-10

### Highlights
- **Animation Screenplay Format (Agent 1)**: Replaced free-form prose narrative output with industry-standard animation screenplay format. `developed_story.md` now contains proper sluglines (`INT./EXT. LOCATION - TIME`), lean 1–3 line action paragraphs, ALL-CAPS sound effects, formatted dialogue with parentheticals, and montage sequences.
- **Screenplay Format Bible (`assets/screenplay-format.md`)**: New comprehensive reference guide for animation screenwriting conventions, based on master-class analysis of *Swapped* (Netflix/Skydance Animation, dir. Nathan Greno).
- **Deterministic Screenplay Validator (`--schema screenplay`)**: Added `validate_screenplay()` checking sluglines, prose walls, dialogue cues, sound cues, and required metadata sections.
- **Downstream Screenplay Authority**: Agents 2, 3, and 5 now extract scene boundaries, dialogue, acting beats, and foley cues directly from the screenplay rather than inventing them.

### Added
- `assets/screenplay-format.md` — Animation Screenwriting Bible with format rules, anti-patterns, and few-shot examples from `Research/ollie`.
- `validate_screenplay()` in `tools/validators.py` — deterministic screenplay format validator.
- `--schema screenplay` registered in `scripts/validate.py`.
- `tests/test_screenplay_validator.py` — 8 unit tests for screenplay validation.

### Changed
- `prompts/story_developer.md` — Agent 1 now requires screenplay format; validation step added before beat board.
- `prompts/scene_writer.md` — Agent 2 uses screenplay sluglines as canonical scene boundary anchors.
- `prompts/storyboard_planner.md` — Agent 3 extracts dialogue, acting beats, and sound cues from screenplay.
- `prompts/video_prompter.md` — Agent 5 harvests ALL-CAPS sound cues into `foley_and_sfx` stem.
- `SKILL.md` — Version bumped to 4.2.0; Agent 1 section updated with screenplay validation.
- `ARCHITECTURE.md` — Agent 1 validator updated from `None (free-form)` to `--schema screenplay`.

---

## [4.1.0] - 2026-09-10

### Highlights
- **Script Intake Normalizer (`Agent 1`)**: Added `preserve_script` intake mode allowing authored screenplays (e.g. *Kutty Karupu*) to be processed without destructive rewriting or scene flattening, alongside duration modes (`preserve_script`, `compress`, `expand`, `exact`).
- **Canonical Machine-Readable Dual Models**: Added companion `story.json` entity and constraint manifest alongside human-readable markdown files.
- **Critique Gate (GATE 0) Severity Tiers**: Replaced circular PASS/FAIL auditing with `BLOCKER`, `MAJOR` (with required `Disposition: RESOLVED | ACCEPTED_AS_INTENDED`), `MINOR`, and `NOT_APPLICABLE` filtering.
- **Approved Render Manifest (`render_manifest.json`)**: Added `scripts/build_manifest.py` and sha256 checksum staleness checks in `scripts/render_all.py` to prevent accidental GPU execution on stale or modified artifacts.
- **Storyboard Template Consolidation**: Consolidated `prompts/storyboard_sheet_template.md` and `prompts/image_prompter.md` with proven 9-panel prompt principles (plain prose reading order, Reference Priority hierarchy, Action Contract for static poses, and Final Continuity Checklist).
- **Discrepancy Authority & 4-Layer Audio Hierarchy**: Established clear authority rules (sheet = visual authority; storyboard = editorial authority) and formalized audio sections into `diegetic_dialogue`, `foley_and_sfx`, `environmental_ambience`, and `non_diegetic_music`.
- **Deterministic Validators**: Added `--schema constraints` and `--schema manifest` to `scripts/validate.py` and `tools/validators.py`.

---

## [4.0.0] - 2026-09-09

### Highlights
- **Directorial & Cinematography Discipline**: Transitioned from rigid micro-shot slicing to dynamic, director-led shot depth planning (master takes, asymmetric two-shots, action arcs).
- **Anime Studio Playbook**: Integrated production metadata for animation styling, layout composition, and visual motifs into the core scene schema.
- **H3-Native Style LoRAs**: Added official presets, installation scripts, and ComfyUI workflow support for stylized aesthetics (storybook, flat geometric, vintage editorial, concept art).
- **Refined Ref2VA Prompting Contract**: Formalized the 6-section MiniMax H3 reference-to-video-audio prompt specification with strict word budgets, 3D camera motion syntax, and facial fidelity rules.

### Added
- **Production Asset Guides (`assets/`)**:
  - `anime-studio-playbook.md`: Guides staging, layouts, acting beats, and visual continuity for animated storytelling.
  - `cinematography-bible.md`: Authoritative reference for focal lengths, camera movement mechanics, shot progression, lighting moods, and spatial framing.
  - `minimax-h3-modes-guide.md`: Detailed guidance on MiniMax H3 operational modes, prompt weights, and reference conditioning limits.
  - `style-lora-presets.md`: Tested parameter configurations, trigger keywords, and strength brackets for H3 style LoRAs.
  - `ref2va-format.md`: Reference contract for multi-modal H3 reference inputs and prompt structuring.
- **Templates & Prompts (`prompts/`)**:
  - `character_sheet_realistic_template.md`: Dedicated template for realistic/live-action character Turnaround Sheets.
  - Stage A3-Pre in `SKILL.md`: Director's prerequisite for **Dynamic Shot Depth & Duration Planning** (Continuous Master Takes 10–15s, Asymmetric 2-Shots, Dynamic Action Arcs, and Rapid Montages).
- **Scene Schema Fields**:
  - Five new metadata keys per scene in `scene_writer.md`: `style_target`, `acting_beat`, `layout_strategy`, `visual_motif`, and `sound_world`.
- **Validation & Test Suites (`tests/` & `tools/`)**:
  - `tests/test_focus_validator.py`: Validates camera focus statements and depth-of-field constraints.
  - `tests/test_style_lora_workflow.py`: Automated verification of H3 ComfyUI LoRA graph patching.
  - 9 evaluation categories in `directing-questions.md` (200+ checks expanding across Story, Camera, Composition, Animation, Sound, Spatial, and H3 Anime Production).

### Changed
- **`SKILL.md` & `ARCHITECTURE.md`**:
  - Updated output layout targets to `outputs/story-maker-v4/<story>/epi-N/`.
  - Added warnings against tag stuffing and shallow descriptions in Ref2VA video prompts.
  - Standardized seamless continuation phrasing for multi-generation scene chains (`g2+`).
- **Prompt Engineering (`prompts/video_prompter.md`)**:
  - Enforced "One Job" rule across reference assets.
  - Targeted 350–500 words in `detailed_description`.
  - Prioritized medium close-up (MCU) and close-up (CU) framing for key acting/vocal beats to preserve facial fidelity in MiniMax H3.
  - Formalized 3D camera motion syntax: `[Motion Type] with [amplitude] at [speed]`.
- **Validators (`tools/validators.py`, `tools/spatial_prompt_builder.py`)**:
  - Enhanced schema validators for video prompt sections, shot timestamp continuity, and transition grammars.
  - Strengthened spatial plan coordinate contracts and orientation validations.

---

## Comparison: Version Differences

| Feature / Dimension | `story-maker-v3` | `story-maker-v4` | `story-maker-v4p` |
| :--- | :--- | :--- | :--- |
| **Release Base** | Initial MiniMax H3 R2V migration (replaced LTX 2.3) | Director's brief & anime-studio production pipeline | Panorama / 360° background consistency variant |
| **Pacing Strategy** | Rigid micro-shot focus (5–8 micro-shots / 15s, 1.5–3.0s each) | **Dynamic Shot Depth** (10–15s oners, asymmetric 2-shots, dynamic arcs) | Pacing baseline with room-rotation alignment |
| **Scene Metadata** | Basic beats, target durations, characters, locations | Adds `style_target`, `acting_beat`, `layout_strategy`, `visual_motif`, `sound_world` | Standard beat & location metadata |
| **Style LoRAs** | None (pure base model prompting) | **Native H3 Style LoRAs** (storybook, flat geometric, vintage, painterly) | Base model prompting |
| **Cinematography & Playbooks** | Standard director's guide (7 review sections) | **Cinematography Bible**, **Anime Playbook**, **H3 Modes Guide** (9 review sections) | Director's guide + official vendored MiniMax guides |
| **Background Continuity** | Soft tail-video conditioning (`--tail-ref-seconds 3.0`) | Soft tail-video conditioning + spatial planning contracts | **360° Background Video Sweep** (`tools/background_extractor.py`) & cardinal wall plate extraction |
| **3D / Layout Blocking** | 2.5D coordinate landmarks | 2.5D coordinate landmarks + dynamic camera staging | 2.5D coordinates + optional Blender gray clay blocking advice |
