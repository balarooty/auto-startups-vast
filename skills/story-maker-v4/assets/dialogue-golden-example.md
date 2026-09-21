# Dialogue Golden Example — Before & After

Real defects from `outputs/story-maker-v4/clockwork-dumpling/epi-1` and their
P1-standard rewrites. Every dialogue tag in the pipeline must survive
`lint_dialogue_tag()` (the `video_prompt` validator enforces this).

---

## Before 1 — silence as an empty dialogue tag (H3 speaks "dot dot dot")

```
Master Bao (S1) glares in absolute silence: <d>[English] ...</d>
Pip (S2) holds her breath in terrified silence: <d>[English] ...</d>
```

**After** — silence is direction, not speech:

```
Neither character speaks. Master Bao stands frozen, brass tongs held aloft, his
mustache bristling; Pip stays pinned-flat and trembling on the counter.
Audio:
- diegetic_dialogue: None
- foley_and_sfx: The faint tremble of Pip's whiskers; a single drop of condensation falls.
- environmental_ambience: Dead acoustic vacuum, dialogue forward when it returns.
- non_diegetic_music: Silence — total.
```

## Before 2 — a non-verbal sound inside a dialogue tag (spoken as the word "gasp")

```
Master Bao (S1) and Pip (S2) gasp simultaneously in frozen shock: <d>[English] [Gasp!]</d>
```

**After** — vocalizations live in foley, lines in the tag:

```
Both characters freeze mid-motion, chests seizing. A sharp synchronized gasp
escapes them, then nothing.
Audio:
- diegetic_dialogue: None
- foley_and_sfx: One sharp synchronized double gasp, then held breath.
- environmental_ambience: Room tone drops to near silence.
- non_diegetic_music: Silence — total.
```

## Before 3 — the same line delivered twice in one shot

```
Pip (S2) cries out, <d>[English] Ethan!</d> as she slides into the glowing chute.
Audio: ...Lily (S2) cries out, <d>[English] Ethan!</d>, echoing whoosh into the chute.
```

**After** — one canonical placement (the Audio block), the prose describes it:

```
Lily cries out as she slides feet-first into the glowing chute, her voice
bouncing off the limestone walls.
Audio:
- diegetic_dialogue: Lily (S2) cries out, <d>[English] Ethan!</d>, dialogue forward
- foley_and_sfx: Cloth scrape on stone, sudden drop in air pressure.
- environmental_ambience: Echoing chute acoustics, faintly carrying her voice.
- non_diegetic_music: Wonder-struck harp glissando, slow tempo.
```

**Why:** the validator errors on duplicates — one placement, always the Audio
block; the prose references the cry without quoting it again.
