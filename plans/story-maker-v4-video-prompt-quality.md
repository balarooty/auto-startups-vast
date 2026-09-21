# Story Maker V4 — Video Prompt Quality Fix

**Status:** ✅ implemented + tested — P1 (validator), P2 (templates), P3 (gate), P4 (golden + corpus sweep). Released as story-maker-v4 **4.4.0**.
**Target:** `skills/story-maker-v4/` — Agent 5 (`prompts/video_prompter.md`), the
`video_prompt` validator, and the H3 prompt bible.
**Problem:** generated video prompts pass structural validation but are not
*qualified* enough — they produce mediocre H3 renders despite "passing".

---

## 1. Research basis

Two primary online sources, cross-checked against the repo's real outputs:

**A. MiniMax official H3 handbook** (via XiaoHu analysis, Aug 2026):
- The master formula: **reference material description (what each asset DOES) +
  core creative concept (one sentence) + visual process description (what happens
  every second)**. All three are mandatory.
- Camera moves must be **decomposed into primitives**: don't write "orbit shot" —
  write `truck left + pan right`.
- H3 wants **detailed prohibitions** — official exemplars spend a large share of
  the prompt on "don't want" (no new character appearing, no subtitles, no style
  drift). Prohibitions close off failure modes before they happen.
- Music suppression requires an explicit close (`non-diegetic music: N/A`).
- Beat-sync ("groove") rules: bind audio events to **concrete on-screen actions**,
  never "sync to the beat" vaguely.

**B. "7 AI Video Prompt Mistakes" (PixVerse, cross-model tested Jun 2026):**
1. Prompt length ≠ control — the opening line carries the most weight; front-load
   subject/action/location.
2. "Cinematic" is not a quality switch — use visible film language instead.
3. **Never stack multiple camera movements in one shot** — commit to one motion path.
4. Fake negative prompts don't work in standard prompt boxes — prefer positive
   constraints ("hands remain natural"). *(Note: H3 is the exception — its official
   handbook endorses explicit prohibitions, so for H3 we keep a guardrail block but
   phrase items positively where possible.)*
5. "Fast" is not a speed instruction — use physical motion detail.
6. **Don't re-describe a reference image you've already uploaded** — the prompt
   should supply what the image can't: motion, camera, lighting changes, audio.
7. Generic quality words ("masterpiece", "high quality") dilute attention.

---

## 2. Diagnosis — what's actually wrong in our outputs

Inspected `outputs/story-maker-v4/crunchools-noodles/epi-1/video_prompts/s1_g1.txt`
(a passing prompt) and compared against guidance + validator coverage:

| # | Defect | Evidence | Research rule violated |
|---|--------|----------|------------------------|
| D1 | **Identity re-description bloat**: ~100-word appearance paragraphs per character in every generation prompt | crunchools s1_g1: Rin/Bram paragraphs ≈ 200 words of wardrobe detail | B-6 (re-describing the reference); A (refs carry identity; text supplies motion/camera/audio) |
| D2 | **Banned panel references still appear**: "matching Panel 1 of the storyboard" | crunchools s1_g1 SHOT 1 & 4; explicitly banned in `video_prompter.md` rule 5 but never enforced | internal contract |
| D3 | **4-layer audio not used**: prompts carry flat `Audio:` one-liners; `video_prompter.md` mandates diegetic_dialogue / foley_and_sfx / environmental_ambience / non_diegetic_music | crunchools s1_g1 all shots | internal contract; A (audio must be explicit or H3 invents it) |
| D4 | **Style can contradict the episode**: "Cinematic live-action photorealism… photorealistic skin texture" in an animation pipeline | crunchools s1_g1 style block | A; Phase-2 style_bible has no hook into video prompts |
| D5 | **Stale "15.0 seconds" hardcode** in `video_prompter.md` rule 4 ("summing strictly to 15.0 seconds per generation") — but v4 supports 5–20s generations | `prompts/video_prompter.md:145` | internal consistency |
| D6 | **Compound camera moves** ("Push In tracking the cleaver blade…") — two motion ideas in one shot | crunchools s1_g1 SHOT 3 | B-3 (single motion path); A (decompose to primitives) |
| D7 | **No per-second process density**: 3.5–4s shots described in one flat sentence; H3 wants "what happens every second" | crunchools s1_g1 shots | A (visual process description); Phase-2 timing_sheet is never enforced into the prompt |
| D8 | **motion_profile never verified in prompts** (Phase 1 field; Agent 5 instruction added, but no validator check) | — | internal contract |
| D9 | **Word-band mismatch**: validator warns only <120 or >650 timeline words; the bible says 350–500; subject_definitions has no budget at all | `tools/validators.py` ~1461 | B-1, B-7 |
| D10 | **No qualitative gate on prompts**: Agent 5 authors → structural validator → GATE 2. Nothing reviews prompt *quality* (only structure) before paid render | pipeline | A/B both: review before spend |

---
## 3. Fix plan

### P1 — Quality checks in the video_prompt validator (`tools/validators.py`)

Extend `validate_video_prompt_brief` (Director's Brief path) with enforcement for
rules that today are guidance-only:

1. **Panel-reference ban (D2) → ERROR.** Regex `\b[Pp]anel\s*\d+` inside Timeline
   shot bodies errors: "describe the cinematic scene directly, not the panel."
2. **4-layer audio (D3) → ERROR.** Each shot's `Audio:` block must contain the
   four keys `diegetic_dialogue`, `foley_and_sfx`, `environmental_ambience`,
   `non_diegetic_music` (values may be `None`/`Silence`). Flat one-liners fail.
3. **Subject-definition budget (D1) → WARN >60 words / ERROR >120** per character
   paragraph in `subject_definitions`. Forces the slim-anchor pattern (P2).
4. **Single motion path per shot (D6) → WARN.** If one shot's camera sentence
   contains 2+ distinct terms from `MINIMAX_MOTION_TERMS`, warn: commit to one
   move, or decompose into primitives explicitly (`truck left + pan right`).
5. **Style consistency (D4) → WARN/ERROR.** When `<run_dir>/style_bible.md`
   exists, the prompt's style declaration must not contradict
   `production_target` (e.g. bible says 2D anime but prompt says "photorealistic"
   → error). Reuse `parse_style_bible`.
6. **Per-second density (D7) → WARN.** Shots longer than 4.0s whose body has
   fewer than 2 action sentences get: "describe what happens at each second of
   this shot (H3 visual process description)".
7. **motion_profile translation (D8) → WARN.** If the storyboard shot carries
   `motion_profile:`, the shot body must contain at least one mapped phrase:
   `ease_in`→"eases in"/"slow start", `ease_out`→"settles"/"decelerates",
   `on_twos`→"held pose"/"stepped", `follow_through`→"settles"/"overshoot",
   `snap`→"snaps", etc.
8. **Word-band alignment (D9).** Tighten the Timeline band to the bible's
   350–500 (warn outside 300–600), and cap `subject_definitions` total words.

### P2 — Rewrite the prompt template to the official 3-part formula

**Files:** `prompts/video_prompter.md`, `assets/minimax-h3-prompt-bible.md`

1. **Identity anchoring policy (fixes D1).** Replace "Maintain the exact
   appearance of X: [full paragraph]" with:
   - One-line identity anchor per character: name + 2–3 signature visual traits
     (silhouette, palette, one distinctive feature).
   - Then: "Identity, wardrobe, and proportions are carried by the storyboard
     reference image; do not re-describe what the image shows — direct only what
     it cannot: motion, acting beats, camera, lighting changes, audio."
   - Full appearance paragraphs are reserved for characters NOT clearly visible
     in the current sheet (rare; justify in one line).
2. **Restructure to the H3 master formula:** (a) reference material description —
   what `<Picture 1>`/`<Video 1>`/each asset DOES; (b) one-sentence core creative
   concept; (c) Timeline = per-second visual process description.
3. **Camera decomposition rule (fixes D6):** ban compound move names; every shot
   commits to ONE motion, expressed in primitives when needed.
4. **Prohibition block (H3-endorsed):** keep and *expand* the guardrail block —
   detailed don't-wants for this generation (no new characters appearing, no
   style drift mid-shot, no subtitles/text, no duplicate props). Frame items
   positively where possible ("hands remain natural").
5. **Fix the stale 15.0s hardcode (D5)** — durations sum to the generation's
   `duration_seconds` (5–20s), not a fixed 15.
6. **Require timing-sheet compilation (D7):** when
   `timing_sheet_<scene>_g<gen>.md` exists, shots >4s must show second-level beat
   progression ("0–1s …, 1–2s …") sourced from the sheet rows.

### P3 — Quality gate before GATE 2 (D10)

**Files:** `assets/directing-questions.md` (new Section 10), `prompts/critique_agent.md`, `SKILL.md`

- Add **Section 10: Video Prompt Quality (~15 questions)** — one per D-rule:
  identity bloat, panel references, 4-layer audio, style consistency, single
  motion path, per-second density, motion_profile translation, word budget.
- Run as a lightweight Agent 5b self-review over `video_prompts/*.txt` during
  Stage C-Lock, before `build_manifest.py --approve`. Structural validator stays
  the hard gate; Section 10 is the craft review.

### P4 — Golden example + regression corpus

- Rewrite one real prompt (crunchools `s1_g1.txt`) to the new standard as a
  before/after golden pair in `assets/` (referenced by `video_prompter.md`).
- Add `tests/test_video_prompt_quality.py` covering each new P1 check.
- Re-validate the existing `outputs/story-maker-v4/*/video_prompts/` corpus with
  the new validator to size the warning surface (report only — existing approved
  runs are not rewritten).

### Rollout order

P1 (validator) → P2 (templates) → P3 (questions/gate) → P4 (golden + corpus sweep).
All validator additions are error-graduated: new rules start as WARN except the
panel-reference ban and 4-layer audio, which are already written as mandatory in
`video_prompter.md` (so ERROR is consistent with the documented contract).

