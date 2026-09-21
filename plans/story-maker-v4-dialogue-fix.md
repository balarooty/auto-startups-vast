# Story Maker V4 — Dialogue Production Fix

**Status:** ✅ implemented + tested — P1 (lint), P2 (voice bible), P3 (dialogue pass), P5 (mix ranking), P4 (voice anchoring). Released as story-maker-v4 **4.5.0**.
**Target:** `skills/story-maker-v4/` — dialogue flows through Agent 1 (screenplay) →
Agent 3 (storyboard `dialogue:`) → Agent 5 (video prompt `<d>` tags + 4-layer audio).
**Problem:** dialogue is our weakest output — quality varies per scene, voice
consistency across generations is uncontrolled, and real prompts contain
machine-visible dialogue bugs.

---

## 1. Research basis

**A. MiniMax H3 native-audio guidance** (forvideo.ai H3 audio guide, Aug 2026):
- H3 generates stereo dialogue, ambience and music **in-pass**; the prompt fully
  controls it.
- **Voice reference clips**: attaching an `<Audio N>` clip makes a character speak
  in that exact voice — "ideal for consistent brand narrators across a campaign",
  and reference audio is **billed free**. Voice transfer beats describing a voice.
- Common problems → fixes:
  - *Words mumble/drift* → shorten the line + add a delivery note ("calm",
    "urgent whisper").
  - *Ambience overwhelms dialogue* → explicitly rank layers ("dialogue forward,
    faint street noise").
  - *Accent/pronunciation off* → use a voice reference clip, not a description.
- Human review of audio before publishing is recommended even by practitioners.

**B. Animation dialogue craft** (writeforanimation.com — Pixar/Disney writers):
1. **Scene intent first** — write from what the scene wants, not what people say
   (Brenda Chapman, *Brave*).
2. **Subtext** — characters say one thing while their bodies say another
   (Mike Jones, *Soul/Luca*). Best dialogue is slightly impulsive/unfiltered
   (Khalia Amazan, *The Spider Within*).
3. **Economy** — natural, brief, simple; test in a story reel and cut what sounds
   wrong (Chapman). (Our Phase-3 animatic now gives us exactly this reel test.)
4. **The cover-up-names test** (Mckenna Harris, *Ciao Alberto*): hide the character
   names and you should still know who's speaking — every character must have a
   distinct way of communicating.

---

## 2. Diagnosis — real defects found in our outputs

Inspected dialogue across `outputs/story-maker-v4/*/video_prompts/*.txt` (194 `<d>`
lines). Defects:

| # | Defect | Evidence in corpus | Research rule |
|---|--------|--------------------|---------------|
| D1 | **Empty dialogue tags for silence**: `Master Bao (S1) glares in absolute silence: <d>[English] ...</d>` | clockwork-dumpling | H3 will try to *speak* the ellipsis. Silence must be directed as no-speech, not an empty `<d>` tag |
| D2 | **Non-verbal sounds inside `<d>` tags**: `<d>[English] [Gasp!]</d>` | same file | `[Gasp!]` gets *spoken as the word "gasp"* — vocalizations belong in foley, not the dialogue tag |
| D3 | **Dialogue duplicated in both prose and the Audio block** — same `<d>` line twice per shot | easter/genesis outputs ("Audio: ... Lily (S2) gasping: <d>... Huh? ...</d>" repeating the prose line) | risks double delivery / conflicting instruction |
| D4 | **No voice bible** — each character's speech pattern, vocabulary, rhythm, and taboos are re-invented per scene | agents improvise per generation | B-4 (cover-up-names test) |
| D5 | **No voice timbre anchoring** — H3's free `<Audio N>` voice-reference feature is never used; voice is re-described ad hoc ("gravelly culinary authority" in one gen, potentially different in the next) | prompt bible mentions `<Audio N>` but the pipeline never attaches one | A (voice transfer > description) |
| D6 | **No dialogue/ambience ranking** in the 4-layer audio block — nothing tells H3 to keep dialogue forward | all prompts | A ("dialogue forward, faint street noise") |
| D7 | **No deterministic dialogue lint** — nothing rejects empty tags, bracketed sounds, repeated lines, or over-long lines at the prompt level (timing-sheet word-rate check exists but only when a sheet is authored) | validators | tooling gap |
| D8 | **No dialogue pass** — Agent 1 writes dialogue inline while structuring the whole screenplay; there is no dedicated rewrite-for-voice step, and no read-aloud/economy test | pipeline structure | B-1, B-3 |

---
---

## 3. Fix plan

### P1 — Dialogue lint (deterministic, `tools/validators.py`)

New shared helpers used by the `video_prompt`, `screenplay`, and `timing_sheet`
schemas:

1. **Empty/placeholder tags → ERROR.** A `<d>` tag whose content is empty, `...`,
   or punctuation-only errors with the fix: direct silence as `diegetic_dialogue:
   None` + a foley/ambience beat, never an empty dialogue tag.
2. **Bracketed vocalizations inside `<d>` → ERROR.** `<d>[English] [Gasp!]</d>`
   moves to `foley_and_sfx` ("a sharp gasp") — the tag would be spoken literally.
3. **Duplicate line within a generation → ERROR.** The same `<d>` text appearing
   twice (prose + audio block, or two shots) is flagged; one canonical placement
   per line (the Audio block, per the 4-layer contract).
4. **Anti-repetition across cuts → WARN.** Identical or near-identical lines in
   adjacent shots (the "He broke it! / No! He broke it!" pattern) warn with the
   authority-pivot guidance from the unbound guide.
5. **Line fits the shot → ERROR.** Word count of each `<d>` line vs its shot
   duration at ~2.5 words/sec (same rule as the timing sheet, enforced at the
   prompt level so it holds even without a timing sheet).
6. **Dialogue-forward ranking → WARN.** A shot with dialogue whose Audio block
   never ranks it ("dialogue forward", "voice forward") warns.

### P2 — Voice Bible (new artifact, Agent 1)

New `prompts/voice_bible.md` template + new validator schema `voice_bible`:

- Per character: **voice description for H3** (pitch, timbre, pace, accent),
  **speech pattern rules** (sentence length, contractions, interruptions),
  **signature vocabulary / catchphrases**, **taboo phrases** (what they'd never
  say), **2–3 sample lines**, and **relationship registers** (how they talk to
  each other character).
- Validator: one entry per `char_NN` in `developed_story.md`; each entry requires
  all fields; sample lines must pass the same lint as P1.
- Agent 1 authors it alongside `developed_story.md`; Agents 2/3/5 must match it.
  The cover-up-names test (B-4) becomes a critique question.

### P3 — Dedicated dialogue pass (Agent 1c)

New `prompts/dialogue_pass.md` + Stage A step between beat board and scenes:

1. Load screenplay + voice bible.
2. Rewrite every dialogue line against the voice bible: scene intent first,
   subtext over statement, economy (cut anything that doesn't earn its seconds),
   character-distinct rhythm.
3. **Read-aloud proxy**: run each line through the line-length/fit lint; flag
   anything that can't be spoken naturally in its slot.
4. Output stays in `developed_story.md` (screenplay updated in place); validate
   screenplay again after the pass.

### P4 — Voice timbre anchoring (optional, render layer)

H3 accepts free reference audio. Add optional `assets/voices/<cid>.wav` support:

- `config.py`: `VOICE_REFS_ENABLED` flag; `tools/minimax_workflow.py`: attach
  `ref_audios` when a voice file exists for a speaking character.
- Source of the clips: user-provided, or generated locally (macOS `say` with a
  configured voice as a draft; a real TTS/voice-clone pass later).
- Prompt side: `subject_definitions` names `<Audio 1>` per speaker and assigns it
  the vocal-timbre job (the "One Job" rule already in the bible).
- Skipped cleanly when no voice files exist (current behavior preserved).

### P5 — Audio mix ranking convention

Update `prompts/video_prompter.md` 4-layer audio block: when dialogue is present,
`environmental_ambience` and `non_diegetic_music` must carry an explicit rank
("dialogue forward", "ambience faint under dialogue") per H3's mumble fix.

### Rollout order

P1 (lint — catches today's bugs) → P2 (voice bible) → P3 (dialogue pass) →
P5 (ranking) → P4 (voice refs, optional hardware/pipeline work).

### Testing

- New `tests/test_dialogue_lint.py`: empty tags, bracketed sounds, duplicates,
  cross-cut repetition, word-rate fit, ranking warn.
- New `tests/test_voice_bible.py`: schema + per-character coverage.
- Golden fix: rewrite the clockwork-dumpling silence/gasp shots to the new
  standard as a before/after example.

