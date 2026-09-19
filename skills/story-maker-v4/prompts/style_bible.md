# Style Bible — <Episode Title>

> Authored by Agent 1 (Story Developer). This is the per-episode **art-direction
> lock**: every scene's `style_target`/`visual_motif` and every image/storyboard
> prompt must agree with it. Never name a studio or brand — express style as craft.
> Validate: `python3 scripts/validate.py style_bible.md --schema style_bible --run-dir <run_dir>`

production_target: <concrete craft target — e.g. "expressive 2D anime, clean silhouettes, painted gouache backgrounds, limited-animation accents">
palette_script: <the emotional color arc across the episode in one line>
shape_language: <recurring shapes and what they mean — e.g. "circles = safety, sharp angles = threat">
line_weight: <outline treatment — e.g. "thin clean lines, bold on heroes, tapering on motion">
background_treatment: <how backgrounds are rendered vs characters>
lighting_rules: <key/fill direction, time-of-day logic, rim/halo rules>
texture_grain: <grain, halation, cel shading, brushwork>

## Palette Script

One row per scene — the dominant palette + the emotional note it carries.

- scene_id: s1 | colors: <palette> | emotion: <note>
- scene_id: s2 | colors: <palette> | emotion: <note>

## Do / Don't

Explicit exclusions that keep the episode visually coherent. These are enforced:
a scene whose `style_target` or `visual_motif` contradicts a DON'T is flagged.

- DO <positive rule>
- DON'T <exclusion — e.g. "photorealistic skin pores", "neon palette", "lens flare">
