# Agent 1c — Dialogue Pass (rewrite-for-voice)

**Input:** `<run_dir>/developed_story.md` (the screenplay),
`<run_dir>/voice_bible.md` (Agent 1), `<run_dir>/beat_board.md` (Agent 1b).
**Output:** `developed_story.md` updated **in place** — dialogue rewritten, action
lines intact. Then re-validate:
`python3 scripts/validate.py developed_story.md --schema screenplay`

## Job

Run once after the beat board exists and before scenes are broken out. This is
the dedicated **rewrite-for-voice** step: the screenplay's first-draft dialogue
was written while structuring the whole story; now every line gets a craft pass
against the voice bible, before downstream agents freeze it into storyboards and
video prompts.

## The pass, line by line

1. **Scene intent first.** For each scene, restate what the scene wants (its
   visible goal and the emotional point). A line exists because the scene needs
   it — if removing a line doesn't damage the beat, delete it.
2. **Subtext over statement.** Characters say one thing while their bodies say
   another. Never let a character explain their feelings; cut any line that
   narrates emotion ("I'm so angry right now") and let the action line show it.
3. **Voice bible lock.** Each line must match the speaker's `speech_pattern`,
   `signature_vocabulary`, and `registers`. Use their taboos — a character who
   "never apologizes first" must not apologize first.
4. **Economy.** Spoken rate ceiling ~2.5 words/sec against the slot the line will
   occupy. Short lines read better and lip-sync better: prefer "Give it back!
   It's my turn!" over "Please return that to me, it is my turn to play."
5. **Cover-up-names test.** Hide the character cues and read the exchange — you
   must still know who is who. If two characters are interchangeable, rewrite
   both (the validator warns on near-identical voice-bible speech patterns).
6. **Anti-repetition.** No repeated accusations across cuts; when an authority
   figure enters, characters pivot to a plea/bargain, and the authority answers
   with knowing swagger.
7. **Rhythm (parentheticals).** Keep performance direction in the parenthetical —
   delivery, emotion, physicality, `(beat)` — per
   [`assets/screenplay-format.md`](../assets/screenplay-format.md) Section 5.
8. **Lint.** No empty `<d>` placeholders, no bracketed vocalizations inside
   dialogue (gasp/sigh/laugh live in action lines as sound cues).

## Read-aloud proxy

For every dialogue line, apply the deterministic check now, before the pipeline
does: count words, compare against the slot it will likely occupy (beats are
`estimated_seconds` in the beat board). A line that cannot be spoken naturally
at that rate gets shortened or split.

## Rules

- Rewrite dialogue **only** — do not restructure scenes, renumber beats, or
  change the story. Action lines change only where a line was deleted.
- The screenplay must still pass `--schema screenplay` after the pass.
- Silence is direction: a held pause with no line is often stronger than a line.
