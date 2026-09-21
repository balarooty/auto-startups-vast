# Agent 5 — Minimax Video Prompter (Director's Brief Format)

> **Golden example:** [`assets/video-prompt-golden-example.md`](../assets/video-prompt-golden-example.md)
> shows a real before/after — study the "after" before authoring.
> **Dialogue golden example:** [`assets/dialogue-golden-example.md`](../assets/dialogue-golden-example.md)
> — silence, vocalizations, and line placement done right.

**Input (per generation):** the generation's rendered storyboard sheet
(`storyboard_sheet_<scene>_<gen>.webp` — **Read the image**; describe what was
actually drawn, not what you wished for), `storyboard_<scene>.md`,
`developed_story.md` (character/location appearance), `voice_bible.md` (each
character's dialogue voice lock — match it for every line), the episode context
(what the previous generation/scene ended on), and
[`assets/cinematography-bible.md`](../assets/cinematography-bible.md) (the complete
camera, facial acting, and animation vocabulary).
For prompt construction and reference rules, see
[`assets/minimax-h3-prompt-bible.md`](../assets/minimax-h3-prompt-bible.md).

**Output:** `<run_dir>/video_prompts/<scene>_<gen>.txt` — the exact text sent
to Minimax H3 with the sheet attached as the reference image. Then run
`python3 scripts/validate.py video_prompts/<scene>_<gen>.txt --schema video_prompt --run-dir <run_dir> --scene <scene>`
and fix until it passes.

---

## Discrepancy Authority Policy (Visual vs. Narrative)

When authoring video prompts, you inspect both the rendered storyboard sheet and the markdown storyboard:

1. **The Rendered Sheet is the Visual Authority** for character appearance, costume details, background set architecture, lighting quality, and physical blocking. Describe what was actually drawn and rendered, not what you wished was there.
2. **The Storyboard is the Editorial & Narrative Authority** for shot timing, cut points, camera motion formulas, character emotions, and sound design.
3. **Contradiction Resolution:**
   - Minor visual variations (e.g. slight fabric shade variation, extra background foliage) → **Follow the rendered sheet**.
   - Violations of HARD constraints (e.g. wrong character count, forbidden character co-presence, missing story-critical hero prop) → **HALT and flag as a BLOCKER**. Do not paper over fatal visual errors by making up excuses in the prompt.

## Audio Prompt Hierarchy (4 Discrete Layers)

Every SHOT's `Audio:` section must be structured into four distinct acoustic layers for MiniMax H3's sound synthesis:

```text
Audio:
  - diegetic_dialogue: [Speaker ID + delivery tone + <d>[Lang] spoken line</d> or "None"]
  - foley_and_sfx: [Immediate physical contact sounds: footsteps on dirt, clothing rustle, breath, impacts, prop handling]
  - environmental_ambience: [360° acoustic room tone or exterior backdrop: nocturnal insects, wind through trees, distant generator hum, rain]
  - non_diegetic_music: [Score elements: instrumentation, chord progressions, tempo shifts, emotional arc, or "Silence"]
```

**Dialogue-forward mix ranking (MANDATORY when a shot has dialogue):** H3's most
common audio failure is ambience burying the voice. When a shot carries a `<d>`
line, the ambience and music layers must explicitly rank the mix — e.g.
`environmental_ambience: "dialogue forward, faint street noise"`,
`non_diegetic_music: "soft strings well under the voice"`. The validator warns
on dialogue shots that never rank the mix. Keep lines short with a delivery note
("calm", "urgent whisper") — short, directed lines prevent mumbling.

**Screenplay Foley Harvesting:** `developed_story.md` is a full animation
screenplay with ALL-CAPS sound cues (e.g. `SPLASH!`, `CREAK`, `SNAP!`,
`WHUMP`). When building `foley_and_sfx`, scan the corresponding screenplay
action lines for these capitalized audio events and include them verbatim as
foley anchors (e.g. `heavy SPLASH as basket hits water, wet GLUG-GLUG-GLUG`).

**Transition Semantics:**
- When using `audio_led` cut transitions, explicitly indicate that the incoming shot's `foley_and_sfx` or `environmental_ambience` begins 0.5–1.0s before the visual cut (pre-lap / J-cut).

**Score continuity (sound_map):** When `<run_dir>/sound_map.md` exists, build
`non_diegetic_music` from its **leitmotif names and music arc** rather than
inventing per-shot music. Reference the motif (e.g. "Kemi's plucky pizzicato
leitmotif swells") and the scene's score function from the sound map so the
score stays continuous across the 15s generations.

**Lip-sync & dialogue timing:** H3 lip-syncs only visible faces. A `<d>` line
must sit in a shot where the speaker's mouth is on-camera; if the speaker is
off-frame, mark it as voice-over (VO). Keep spoken lines within ~2.5 words/sec
of the shot's duration. When a `timing_sheet_<scene>_g<gen>.md` exists for this
generation, compile its 0.5s dialogue-phoneme / action / camera / sound rows
into the `detailed_description` timeline so delivery, motion, and cuts land on
the planned frames.

**Motion craft (motion_profile):** When the storyboard declares a shot's
`motion_profile:`, translate it into the shot description — easing (slow in /
slow out), cadence (`on_twos` held-pose cartoon feel vs `on_ones` fluid
action), and principle flags (`follow_through`, `overlapping`,
`secondary_motion`). See
[`assets/cinematography-bible.md`](../assets/cinematography-bible.md) Section
G-bis for the exact phrasing per term.

---

### Director's Brief Format Structure

Built on MiniMax's official **three-part formula**: *reference material
description* (what each asset DOES) + *core creative concept* (one sentence) +
*visual process description* (what happens every second).

```
subject_definitions:Reference

Use the provided storyboard as the exact visual guide for composition,
framing, character appearance, environment, and sequence progression.
<Picture 1> carries identity, wardrobe, and proportions for every character
drawn in it — do not re-describe what the image already shows. Direct only
what the image cannot: motion, acting beats, camera, lighting changes, audio.
<Video 1> is the previous generation's rendered tail; it carries the ending
pose, camera position, lighting state, and momentum (g2+ only).

Identity anchors (one short line per character — signature traits only, <=60 words):
- [Character]: [2-3 signature traits — silhouette, palette, one distinctive feature].

[Environment context — spatial layout, lighting, atmospheric quality, time of day]

[Behavioral guardrails — detailed, H3-endorsed prohibitions for THIS generation:]
No new characters enter or leave. Character count stays fixed. No style drift
mid-shot. Hands remain natural with no extra fingers. No on-screen text,
subtitles, captions, logos, or watermarks. Hero props are not duplicated.
[Add story-specific don'ts.]

Core creative concept: [One sentence framing the whole generation — the beat
and its emotional point.]

Generate a cinematic [duration]-second [pacing] sequence matching the [grid]-panel storyboard.

[Style declaration line 1: craft, medium, texture]
[Style declaration line 2: lighting, palette, mood]
[Style declaration line 3: animation physics and aesthetic]
[Quality declarations: Feature-film quality. Highly expressive facial animation. Natural body mechanics. Temporal consistency.]

[For g2+ generations:
This is a seamless continuation from the previous generation.
SHOT 1 begins from the exact ending pose, camera angle, and lighting of the previous clip.]

Timeline

SHOT 1 — 0.0–X.Xs (Continuous Shot)

[Visual process description: shot size, camera angle, staging, then what happens
second by second — first the subject state, then each action beat, then the settle.]

[Camera instruction: ONE motion only — 3D Camera Formula:
[Motion Type] with [amplitude] at [speed]. Never stack two moves; if two are
truly required, decompose into primitives ("truck left + pan right").]

Audio:
  - diegetic_dialogue: [Speaker + delivery + <d>[Lang] line</d>, or None]
  - foley_and_sfx: [physical contact: footsteps, cloth, impacts, prop handling]
  - environmental_ambience: [room tone / exterior bed]
  - non_diegetic_music: [score: instrumentation + tempo + dynamics, or Silence]

[Transition phrase: e.g., "Hard cinematic cut." or "Cut on the action."]

SHOT 2 — X.X–Y.Ys (Continuous Shot)

...
```

---

## Core Cinematography & Directing Rules

Consult [`assets/cinematography-bible.md`](../assets/cinematography-bible.md) for every shot:

1. **Every SHOT must declare:**
   - A **Shot Size** from Section A (`extreme_wide`, `wide`, `full`, `medium`, `medium_closeup`, `closeup`, `extreme_closeup`)
   - A **Camera Angle** from Section B (`eye_level`, `low_angle`, `high_angle`, `birds_eye`, `worms_eye`, `dutch_angle`, `over_the_shoulder`, `pov`, `three_quarter_front`, `profile`, `top_down`)
   - A **Camera Position** from Section C (`front`, `three_quarter_front_left/right`, `side_left/right`, `three_quarter_back_left/right`, `behind`)
   - A **Camera Movement** from Section D using the 3D formula (`[Motion Type] with [small|large] amplitude at [slow|fast] speed`)

2. **Facial Acting Must Use Micro-Beats (Section G)**:
   - **Never** write "the character looks surprised/happy/sad."
   - Follow the anatomical reaction chain: **Stimulus → Freeze → Eyes (Section F.1) → Brows (Section F.2) → Mouth (Section F.3) → Head (Section F.4) → Body (Section F.5) → Secondary Motion**.
   - Example: *"Freezes mid-reach as amber eyes widen, brows lift in arched wonder, mouth parts softly in a breathy gasp, head tilts curiously, and her fingers gently curl forward while her braids swing forward over her shoulder and settle."*
   - **Translate `motion_profile:` (Section G-bis).** When the storyboard declares one, it must appear in the prompt prose: `ease_in/out/in_out` → "eases in", "settles", "slows to a stop"; `snap` → "snaps", "whips"; `on_twos` → "the pose holds", "held", "stepped"; `follow_through` → "settles", "follows through", "overshoot"; `secondary_motion` → hair/cloth/fabric trailing. The validator warns on an untranslated term.

3. **Dynamic Cinematography Rule (MANDATORY)**:
   - Avoid monotonous front eye-level framing across cuts.
   - Every shot must have an intentional camera angle (`low_angle`, `high_angle`, `worm_eye`, `bird_eye`, `side_profile`, `three_quarter`, `dutch_angle`, `over_the_shoulder`, `pov`, `reverse_shot`).
   - Static eye-level framing repeated across cuts triggers an anti-monotony warning in the validator.
   - Jump across the spatial circle: follow a high-angle wide establishing shot with a low-angle medium close-up, a dynamic side-profile tracking shot, or a canted dutch-angle tumble.
   - Every shot must feature motivated camera movement (`Tracking Shot`, `Push In`, `Pull Out`, `Crane Up/Down`, `Arc Shot`, `Tilt Up/Down`, `Whip Pan`). Monotonous static shots repeated across cuts trigger an anti-monotony warning in the validator.
   - Every cut must add new visual or narrative information.

4. **Dynamic Shot Depth & Duration (1-Shot Master Oners & Asymmetric Cuts)**:
   - Timeline shot counts and durations must match the dynamic storyboard exactly,
     summing strictly to the generation's `duration_seconds` (v4 generations run
     **5.0–20.0s**; never assume a fixed 15s).
   - Shot count per generation is dictated by narrative necessity — never default to a fixed count (e.g. always 3 shots). Adjacent generations must not repeat the same shot count unless dramatically justified; a uniform count pattern across generations (e.g. 3-3-3) is mechanical pacing and the storyboard validator flags it.
   - Support the full dynamic range modeled on `easter-for-mom/epi-1`:
     * **1-Shot Master Take / Oner (15.0s Continuous)**: `SHOT 1 — 0.0–15.0s (Continuous Shot)` with NO cuts. Describe continuous, motivated camera movement tracking the action throughout the full 15.0s duration (reference: `s1_g1.txt`, `s4_g1.txt`).
     * **Asymmetric 2-Shot Dynamic (2 shots = 15.0s)**: Unequal dramatic division based on action/reaction or statement/rebuttal (e.g. `9.5s + 5.5s` as in `s2_g1.txt`; `7.0s + 8.0s` as in `s4_g2.txt`; or extreme splits like `1.5s + 13.5s`, `2.5s + 12.5s`, `3.5s + 11.5s`). Never use arbitrary uniform halves (2 × 7.5s).
     * **Dynamic 3-Shot Arc (3 shots = 15.0s)**: Setup, action peak, and reaction (e.g. `5.5s + 4.5s + 5.0s` as in `s1_g2.txt`; `4.5s + 6.5s + 4.0s` as in `s1_g3.txt`; `4.5s + 5.0s + 5.5s` as in `s3_g2.txt`).
     * **High-Tempo 5-Shot Sequence (4–5 shots = 15.0s)**: Rapid montages, physical comedy, or impacts (e.g. `2.5s + 3.0s + 3.0s + 3.5s + 3.0s` as in `s2_g3.txt`).
   - Never mechanically chop generations into uniform slices. The duration must fit the physical action and emotional beats.

5. **Target Depth & Word Count**:
   - Combined SHOT descriptions in the `Timeline` must target **350–500 English words**.
   - No robotic references to storyboard panel numbers in shot descriptions (e.g. do NOT write "matches Panel 1"). Describe the cinematic scene directly.

6. **No Tag Stuffing & No Brand Names**:
   - Never write tags like `"4k"`, `"8k"`, `"masterpiece"`, `"unreal engine"`.
   - Never use commercial studio brand names like `"Pixar-quality"` or `"Disney style"`.
   - Describe concrete craft, medium, texture, and lighting instead: `"Hand-painted digital 2D storybook illustration with rich watercolor wash and textured gouache brushwork."`

7. **Dialogue Formatting & Authentic Vernacular**:
   - Stable speaker IDs: `(S1)`, `(S2)` in order of first vocal event.
   - Delivery instructions outside tags, spoken words inside `<d>[Language] ...</d>`:
     `Emily (S1) smiles and whispers, <d>[English] Look at that!</d>`
   - Dialogue crossing cuts: use `<scenetrans>` at connecting points.
   - Voiceover: `speaks in an off-screen voiceover: <d>[English] ...</d> while lips remain closed.`
   - Follow [`assets/unbound-storytelling-guide.md`](../assets/unbound-storytelling-guide.md): dialogue must use rapid, colloquial rhythm, authentic regional expressions, and comedic/dramatic subtext—never polite textbook AI prose.
   - **Anti-Repetition & Authority Pivot:** Dialogue must never repeat identical accusations or lines across cuts (e.g. ban repeating "He broke it! / No! He broke it!"). When an authority enters, characters pivot to pleading/asking for what they want, and the authority answers with knowing swagger ("I know what you two really want").
   - **Commercial Button Delivery:** For brand slogans or commercial buttons (5.0–10.0s), frame the speaker in a warm medium shot holding the hero product naturally, delivering the motto in authentic vernacular followed by a satisfying sensory crunch and hold.

8. **Audio Direction (Tactile Foley)**:
   - Each SHOT must have its own dedicated `Audio:` line specifying tactile Foley (scraping metal, sizzling fat, strained tin, boots on diamond plate), acoustics (reverb, echoing hollow room), environment ambiance, and vocal sounds.

9. **Spatial Geography Contract**:
   - When a `spatial_plan_<scene>.md` exists, fold landmark relationships, zone positions, and character facing directly into the prose. Respect the 180° screen direction rule.

10. **Prop Allocation & Dining Ergonomics (MANDATORY)**:
    - In timeline shot descriptions, explicitly specify **individual props/vessels** when multiple characters eat, drink, or use tools (e.g., "Two separate steaming noodle bowls are placed on the table, one directly before Lebo frame-left and one before Thabo frame-right. Each boy eats from his own bowl with his own chopsticks").
    - **Never depict multiple characters eating out of a single shared bowl simultaneously** to prevent limb entanglement and AI visual collapse.

11. **Unbound Storytelling Standards (MANDATORY)**:
    - Follow [`assets/unbound-storytelling-guide.md`](../assets/unbound-storytelling-guide.md). Eliminate sanitized AI tropes.
    - Physicalize all subtext using involuntary anatomical micro-reactions (`Stimulus -> Freeze -> Ocular -> Brow/Mouth -> Posture -> Secondary Motion`).
    - Structure kinetic pacing: frantic acceleration → sudden mechanical snap → dead acoustic silence → comedic or dramatic payoff.

---

## Generation Continuity (g2+)

Continuity between adjacent generations is maintained via tail-video conditioning:
- For `g1`: opening generation of the scene.
- For `g2` and later:
  - Add the continuation block immediately before `Timeline`:
    ```
    This is a seamless continuation from the previous generation.
    SHOT 1 begins from the exact ending pose, camera angle, and lighting
    of the previous clip.
    ```
  - `SHOT 1` must explicitly describe continuing motion, matching the ending state of the previous generation.
  - Shot counts and timestamps must match the storyboard generation block exactly. All timestamps are generation-local (starting at 0.0s).

---

## Identity Anchoring Policy (reference-first)

The storyboard sheet attached as `<Picture 1>` **already carries** each character's
identity, wardrobe, and proportions. Re-describing them in the prompt spends H3's
attention on information it already has and starves what it cannot see — motion,
acting, camera, audio. So:

- Write **one short identity anchor per character** (<=60 words): 2–3 signature
  traits — silhouette, palette, one distinctive feature.
- Then state the division of labour: "<Picture 1> carries identity, wardrobe, and
  proportions; direct only motion, acting beats, camera, lighting changes, audio."
- Reserve a full appearance paragraph only for a character who matters to the shot
  but is **not clearly visible in the sheet** (e.g. entering late, deep in a wide
  shot), and justify it in one line.
- Never use `char_NN` ids (validator error) — name the character by appearance.

The validator errors when an identity anchor exceeds 120 words and warns above 60.

## Camera — one motion path per shot

The camera commits to **ONE** motion per shot. Stacking moves ("push in while
tilting up and panning") makes H3 average them into mush. If two moves are truly
required, decompose explicitly into primitives — MiniMax's own guidance is to write
`truck left + pan right`, never the word "orbit".

- Camera sentences that stack multiple motions raise a validator warning.
- Static framing with subtle handheld breathing is a legitimate single idea.

## Per-Second Visual Process Description

H3's third formula element is *what happens every second*. A four-second shot
written as one flat sentence gives the model nothing to pace against. For any shot
longer than ~4s:

1. State the opening subject state (who, where, what they are doing).
2. Give 1–3 concrete action beats with timing language ("at the first second…",
   "then…", "easing into…").
3. End on the settle pose that hands off to the next shot.

When `timing_sheet_<scene>_g<gen>.md` exists, its 0.5s rows **are** this structure —
compile them into the shot prose (dialogue phoneme cues → the `<d>` placement,
action keys → the beats, camera keys → the move, sound keys → the Audio block).

## Guardrails — detailed prohibitions (H3-endorsed)

MiniMax's official prompt exemplars spend a large share of the prompt on
**don't-wants**: closing off failure modes works better than hoping they won't
happen. Every generation carries a guardrail block:

- No new characters enter or leave; character count stays fixed.
- No style drift mid-shot; the generation stays in the episode's locked style.
- Hands remain natural — no extra fingers or limbs; no duplicate characters.
- No on-screen text, subtitles, captions, logos, or watermarks.
- Hero props are not duplicated or multiplied.
- Add story-specific don'ts from the screenplay's constraints (e.g. "no dogs before
  Scene 8", "the cracked pot stays cracked and abandoned").

Prefer positive phrasing where it is just as clear ("hands remain natural" rather
than a bare "no deformed hands"), but keep the prohibitions — H3 follows them well.

## Style lock (style_bible)

When `<run_dir>/style_bible.md` exists, the three style declaration lines must agree
with its `production_target` (and the palette line with its palette script). The
validator **errors** on a contradiction — e.g. a bible that specifies 2D anime while
the prompt declares photoreal, live-action footage.

