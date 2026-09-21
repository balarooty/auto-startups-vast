# Voice Bible — <Episode Title>

> Authored by Agent 1 (Story Developer) alongside `developed_story.md`. This is
> the episode's **dialogue voice lock**: every line every character speaks must
> match their entry here. Agents 2, 3, and 5 read it before writing or routing
> any dialogue. The gold standard is the **cover-up-names test**: hide the
> character's name on any line — you should still know who is speaking.
> Validate: `python3 scripts/validate.py voice_bible.md --schema voice_bible --run-dir <run_dir>`

## Character: <char_01 — Name>

voice_description: <what the character sounds like for H3 — pitch, timbre, pace, accent; e.g. "mid-pitched, gravelly, unhurried with a coastal drawl">
speech_pattern: <sentence rhythm rules — e.g. "short clipped fragments, drops subjects, never asks two questions in one breath">
signature_vocabulary: <2-5 words/phrases they own — e.g. "flame-tender", "batch o' gold">
taboos: <phrases this character would never say — e.g. "never says please when demanding", "never uses the word 'delicious' — says 'worth dying for'">
sample_lines:
- "<sample line 1 in their voice>"
- "<sample line 2>"
- "<sample line 3>"
registers:
  toward_<other_char>: <how they talk to that character — warmer/sharper/teasing>

## Character: <char_02 — Name>

voice_description: <...>
speech_pattern: <...>
signature_vocabulary: <...>
taboos: <...>
sample_lines:
- "<...>"
registers:
  toward_<other_char>: <...>

## Rules

- Every entry's `sample_lines` must pass the dialogue lint (no empty tags, no
  bracketed vocalizations inside `<d>`, spoken rate <=2.5 words/sec).
- Distinctness: no two characters may share the same `speech_pattern` — if two
  entries read the same, rewrite both until the cover-up-names test passes.
- Dialogue is written from **scene intent**: the line exists because the scene
  wants it, not because the character should talk.
- **Subtext over statement**: characters say one thing while their bodies say
  another; never have a character explain their feelings.
- **Economy**: every line must earn its seconds — if it can be cut without losing
  the beat, cut it.
