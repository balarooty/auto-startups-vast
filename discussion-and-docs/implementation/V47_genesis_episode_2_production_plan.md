# V47: Genesis Beginning — Episode 2 Production Plan (Genesis 2:1-25)

## Overview
Author and validate the complete Stage A & Stage C production pipeline for **Genesis Beginning — Episode 2**, following the established Story Maker V4 H3-directed scene production architecture.

## Story Source: Genesis 2:1-25 (NLT)
1. **The Seventh Day Rest (vv. 1-3)**: Creation completed; God rests from His work on the seventh day and blesses it as holy.
2. **Forming of Man from the Dust (vv. 4-7)**: No rain yet; underground mist waters the ground. The LORD God forms man from the dust of the earth and breathes the breath of life into his nostrils.
3. **The Garden of Eden & The River (vv. 8-15)**: God plants a garden in Eden in the east; grows beautiful fruit trees, with the Tree of Life and Tree of Knowledge of Good and Evil at center; one river divides into four branches (Pishon, Gihon, Tigris, Euphrates). God places Adam in Eden to tend and watch over it.
4. **The Command and Warning (vv. 16-17)**: Permission to freely eat from every tree except the Tree of the Knowledge of Good and Evil ("If you eat its fruit, you are sure to die").
5. **Naming the Animals & Seeking a Helper (vv. 18-20)**: "It is not good for man to be alone." God forms beasts and birds from the ground and brings them to Adam to name them. None is a suitable partner.
6. **Creation of Woman & The Sacred Union (vv. 21-25)**: God puts Adam into a deep sleep, takes one of his ribs, forms woman, and brings her to Adam. Adam's exultant cry: "At last! Bone of my bone and flesh of my flesh!" Both naked and unashamed in innocent harmony.

## Continuity & Framing Architecture
- **Framing Device**: Continues directly from Episode 1's handoff (`epi-1/storyboard_s3.md` end handoff: Elder holding the Storybook in the Lantern Nook). Elder Storyteller (`char_02`) and Grandchild (`char_03`) in the Lantern Nook (`loc_04`). The child turns to the next chapter as the gilded Storybook (`obj_01`) glows warm gold.
- **Visual Style**: High-End Stylized 3D Chibi Storybook Animation (2.5-head-tall proportions, warm hand-painted gouache and watercolor textures over paper grain, warm honey-gold lighting, gentle rim light).
- **Core Cast**:
  - `char_01`: The Creator (kind grandfatherly presence, rounded white beard, cream robe, gold sash, warm golden aura)
  - `char_02`: Elder Storyteller (silver bun, brass spectacles, dusty-rose shawl)
  - `char_03`: Grandchild (6 yo, cowlick, yellow sweater, red-cream scarf, hugging cushion)
  - `char_04`: Adam (young man, clay-brown linen tunic, woven belt, bare feet, leaf behind ear)
  - `char_05`: Eve (young woman, cream and leaf-green dress, long dark hair with white blossom, vine belt)
- **Props & Locations**:
  - `loc_03`: Eden Garden — The Finished World
  - `loc_04`: The Lantern Nook — Storytelling Spot
  - `loc_05`: Eden Riverhead & The Four Streams (New location plate for the branching rivers and valley)
  - `obj_01`: The Storybook
  - `obj_02`: The Tree of the Knowledge of Good and Evil & The Tree of Life

## Episode Structure (Target: 90.0 Seconds)
- **Scene s1 — The Seventh Day & The Breath in the Dust (30.0s, Gen 2:1-7)**
  - `g1 (15.0s)`: Lantern Nook opening → Portal into Eden at sunrise. The Creator rests on the seventh day in calm serenity, blessing the creation as warm mist rises from the ground.
  - `g2 (15.0s)`: The Creator kneels in the rich dark loam, sculpting the dust of the earth with tender hands, and breathes the radiant golden breath of life into Adam's nostrils; Adam gasps in wonder as life ignites.
- **Scene s2 — The Four Rivers & The Sacred Charge (30.0s, Gen 2:8-17)**
  - `g1 (15.0s)`: The Creator walks with young Adam through Eden, showing the river branching into four sparkling waterways (Pishon, Gihon, Tigris, Euphrates); placing Adam to tend and care for the garden.
  - `g2 (15.0s)`: At the heart of Eden, God introduces the lush orchard trees and points to the Tree of Knowledge of Good and Evil, delivering the loving, solemn warning while Adam listens with wide, trusting eyes.
- **Scene s3 — The Animals Named & The Gift of Eve (30.0s, Gen 2:18-25)**
  - `g1 (15.0s)`: "It is not good for man to be alone." God brings the animals and birds to Adam; Adam playfully laughs and names each creature, but realizes none is a match for him.
  - `g2 (15.0s)`: Deep peaceful sleep falls on Adam. God takes a rib and forms Eve in an arc of starlight and blossom petals. Adam awakens to see Eve; joyful exclamation ("Bone of my bone!"); they clasp hands in pure innocent harmony without shame as the Storybook glows in the cozy Lantern Nook.

## Deliverables & Validation Suite
1. `outputs/story-maker-v4/genesis-beginning/epi-2/developed_story.md` (`--schema screenplay`)
2. `outputs/story-maker-v4/genesis-beginning/epi-2/beat_board.md` (`--schema beat_board --target-seconds 90`)
3. `outputs/story-maker-v4/genesis-beginning/epi-2/scenes.md` (`--schema scenes --target-seconds 90`)
4. `outputs/story-maker-v4/genesis-beginning/epi-2/storyboard_s1.md` (`--schema storyboard --scenes-path scenes.md`)
5. `outputs/story-maker-v4/genesis-beginning/epi-2/storyboard_s2.md` (`--schema storyboard --scenes-path scenes.md`)
6. `outputs/story-maker-v4/genesis-beginning/epi-2/storyboard_s3.md` (`--schema storyboard --scenes-path scenes.md`)
7. `outputs/story-maker-v4/genesis-beginning/epi-2/image_prompts/` (characters, locations, objects, storyboard sheets)
8. `outputs/story-maker-v4/genesis-beginning/epi-2/video_prompts/` (s1_g1..s3_g2 Ref2VA video prompts)
9. Full validation pass with zero errors across all artifacts.
