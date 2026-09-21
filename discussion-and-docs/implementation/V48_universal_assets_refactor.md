# V48: Universal Assets Refactoring for Genesis Beginning & Story Maker V4

## Overview
Refactor asset prompt organization in `outputs/story-maker-v4/genesis-beginning` so that characters, locations, and objects are defined universally at the story level (`assets/image_prompts/`), while keeping only episode-specific artifacts (scenes, storyboards, storyboard sheet prompts, and video prompts) inside `epi-1`, `epi-2`, ..., `epi-N`.

## Problem Statement
Currently, character, location, and object prompts are duplicated across episode folders (`epi-1/image_prompts/` and `epi-2/image_prompts/`). This creates maintenance overhead and visual drift when a character or object prompt is updated in one episode but not another.
Furthermore, `skills/story-maker-v4/tools/image_pipeline.py` currently looks only within `run_dir/image_prompts/`. Updating `image_pipeline.py` to check the universal story assets directory (`<story>/assets/image_prompts/`) as a fallback allows episodes to share character, location, and object definitions cleanly.

## Target Directory Layout

```text
outputs/story-maker-v4/genesis-beginning/
├── assets/
│   └── image_prompts/
│       ├── characters/
│       │   ├── char_01.txt (The Creator)
│       │   ├── char_02.txt (Elder Storyteller)
│       │   ├── char_03.txt (Grandchild)
│       │   ├── char_04.txt (Adam)
│       │   └── char_05.txt (Eve)
│       ├── locations/
│       │   ├── loc_01.txt (The Deep)
│       │   ├── loc_02.txt (The Vault)
│       │   ├── loc_03.txt (Eden Garden)
│       │   ├── loc_04.txt (The Lantern Nook)
│       │   └── loc_05.txt (The Riverhead of Eden)
│       └── objects/
│           ├── obj_01.txt (The Storybook)
│           └── obj_02.txt (The Trees of Eden)
├── epi-1/
│   ├── developed_story.md
│   ├── scenes.md
│   ├── storyboard_s1.md
│   ├── storyboard_s2.md
│   ├── storyboard_s3.md
│   ├── image_prompts/
│   │   ├── s1/ (storyboard_sheet_g1.txt, g2.txt)
│   │   ├── s2/ (storyboard_sheet_g1.txt, g2.txt)
│   │   └── s3/ (storyboard_sheet_g1.txt, g2.txt)
│   └── video_prompts/
│       └── s1_g1.txt ... s3_g2.txt
└── epi-2/
    ├── developed_story.md
    ├── beat_board.md
    ├── scenes.md
    ├── storyboard_s1.md
    ├── storyboard_s2.md
    ├── storyboard_s3.md
    ├── image_prompts/
    │   ├── s1/ (storyboard_sheet_g1.txt, g2.txt)
    │   ├── s2/ (storyboard_sheet_g1.txt, g2.txt)
    │   └── s3/ (storyboard_sheet_g1.txt, g2.txt)
    └── video_prompts/
        └── s1_g1.txt ... s3_g2.txt
```

## Planned Code & Asset Changes

1. **`skills/story-maker-v4/tools/image_pipeline.py`**:
   - In `character_prompt_path(run_dir, cid)`, `location_prompt_path(run_dir, lid)`, and `object_prompt_path(run_dir, oid)`:
     - Check local `run_dir/image_prompts/<category>/<id>.txt`.
     - Fall back to story-level universal path `os.path.dirname(run_dir)/assets/image_prompts/<category>/<id>.txt` (and `os.path.dirname(run_dir)/image_prompts/<category>/<id>.txt`).
     - Return canonical default path if neither exists.
2. **`outputs/story-maker-v4/genesis-beginning/assets/image_prompts/`**:
   - Merge all distinct characters (`char_01`–`char_05`), locations (`loc_01`–`loc_05`), and objects (`obj_01`–`obj_02`) into the universal `assets/image_prompts/` folder.
3. **Clean up episode folders**:
   - Remove redundant `characters/`, `locations/`, and `objects/` directories from `epi-1/image_prompts/` and `epi-2/image_prompts/`, leaving only episode-specific `s1/`, `s2/`, `s3/` storyboard sheet prompts, storyboards, and video prompts.
4. **Validation & Verification**:
   - Run `python3 -m pytest skills/story-maker-v4/tests/` to guarantee no regressions in the skill test suite.
   - Run `python3 skills/story-maker-v4/scripts/validate.py` on all `epi-1` and `epi-2` prompts and storyboards to verify clean resolution and pass status.

## Execution & Verification Status (Complete)
- **Code implementation**: Updated `_resolve_asset_prompt_path` in `skills/story-maker-v4/tools/image_pipeline.py`.
- **Unit test**: Added `test_resolve_asset_prompt_path_story_level_assets` to `skills/story-maker-v4/tests/test_phase2.py`. All 233 unit tests pass.
- **Story Consolidation**: Universal prompt assets created under `outputs/story-maker-v4/genesis-beginning/assets/image_prompts/` (`characters/`, `locations/`, `objects/`).
- **Episode Cleanup**: Removed duplicate prompt folders from `epi-1/image_prompts/` and `epi-2/image_prompts/`.
- **Validation**: All scenes and video prompts in `epi-1` and `epi-2` validated and passed with 0 errors via `skills/story-maker-v4/scripts/validate.py`.

