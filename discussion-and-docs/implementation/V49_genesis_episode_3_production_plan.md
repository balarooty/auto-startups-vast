# V49: Genesis Beginning — Episode 3 (Genesis 3:1–24) Production Plan

## Overview
Adaptation of **Genesis 3:1–24** (The Fall, Judgments, Garments of Grace, and The East Gate) into **Episode 3** of the *Genesis Beginning* 3D chibi animation series.

## Episode Metrics
- **Duration**: 90.0 seconds (3 scenes × 30.0s each; 2 generations per scene × 15.0s each).
- **Style**: High-End 3D Chibi / Tactile Gouache Storybook Animation.
- **Framing Device**: Lantern Nook (`loc_04`) with Elder Storyteller (`char_02`) and Grandchild (`char_03`).

## Characters
- `char_01`: The Creator
- `char_02`: Elder Storyteller (Grandmother, ~70)
- `char_03`: Grandchild (6 years old)
- `char_04`: Adam (Young adult man, ~25)
- `char_05`: Eve (Young adult woman, ~25)
- `char_06` (NEW): The Serpent (Cunning, iridescent emerald-gold scales)
- `char_07` (NEW): The Cherub Guardian (Awe-inspiring celestial guardian with radiant golden wings)

## Locations
- `loc_01`: The Deep (Chaos Waters)
- `loc_02`: The Vault (Expanse)
- `loc_03`: Eden Garden (Clearing & Rivers)
- `loc_04`: The Lantern Nook (Framing device)
- `loc_05`: The Riverhead of Eden (Overlook)
- `loc_06` (NEW): The Forbidden Grove (Shadowed boughs of the Tree of Knowledge)
- `loc_07` (NEW): The East Gate of Eden & Wilderness Threshold

## Objects
- `obj_01`: The Storybook
- `obj_02`: The Trees of Eden
- `obj_03` (NEW): The Forbidden Fruit
- `obj_04` (NEW): The Flaming Sword

## Execution & Verification Status (Complete)
- **Universal Assets Created**:
  - `characters/`: `char_06.txt` (The Serpent), `char_07.txt` (The Cherub Guardian with trimmed beard per user instruction)
  - `locations/`: `loc_06.txt` (The Forbidden Grove), `loc_07.txt` (The East Gate of Eden & Wilderness Threshold)
  - `objects/`: `obj_03.txt` (The Forbidden Fruit), `obj_04.txt` (The Flaming Sword)
- **Episode 3 Production Artifacts Created**:
  - `developed_story.md`: Full animation screenplay with sluglines, sound effects, formatted dialogue, character & location registries.
  - `beat_board.md`: 9 beats totaling 90.0s using canonical emotion vocabulary.
  - `scenes.md`: 3 scenes totaling 90.0s with full anime-studio metadata.
  - `storyboard_s1.md`, `storyboard_s2.md`, `storyboard_s3.md`: 3x2 grid storyboard specifications explicitly framing Adam and Eve as adult young man & woman.
  - `image_prompts/s1/`, `s2/`, `s3/`: Storyboard sheet prompts per generation with complete scene, character, prop continuity, and panel directions.
  - `video_prompts/`: 6 MiniMax H3 Ref2VA director's briefs (`s1_g1.txt` ... `s3_g2.txt`) with local 0-15s timestamps and tail references.
- **Validation**:
  - All schemas validated via `validate.py`: 100% PASS with 0 errors and 0 warnings.
  - Full pytest test suite: 233 passed in 0.20s.

