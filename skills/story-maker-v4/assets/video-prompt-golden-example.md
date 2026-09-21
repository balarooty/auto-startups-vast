# Video Prompt Golden Example — Before & After

A worked before/after of a real generation (`crunchools-noodles/epi-1`,
`video_prompts/s1_g1.txt`) showing the P1/P2 standard. The **before** is the
original output; the **after** applies the identity-anchoring policy, 4-layer
audio, single camera motion, per-second process description, and detailed
guardrails. The *after* passes the updated `video_prompt` validator.

---

## BEFORE (what weak prompts looked like)

```
subject_definitions:Reference
...
Maintain the exact appearance of Rin: lean, athletic 19-year-old young man with wavy
honey-brown hair in a loose low ponytail at the nape, soft parted bangs framing temples,
warm hazel-amber eyes with fine crinkles, high cheekbones, fair skin with light natural
freckles across nose bridge, tailored charcoal-brown distressed leather doublet with
vertical harness straps and antique bronze buckles over an unbleached coarse off-white
linen tunic with rolled sleeves, dark brown leather wrist bracers, and fingerless
leather work gloves.
...
SHOT 1 — 0.0–4.0s (Continuous Shot)
An eye-level medium two-shot matching Panel 1 of the storyboard. Rin leans over the
flour-dusted oak butcher block ... Audio: Rhythmic stretching of pliable dough, soft puff
of billowing flour dust, gentle crackle of distant hearth embers.
```

**What's wrong:** ~100-word wardrobe re-description the sheet already carries;
panel-number references; flat one-line audio; compound camera ("Push In tracking
the blade"); 3.5–4s shots described as single flat beats.

---

## AFTER (the P1/P2 standard — passes the updated validator)

```
subject_definitions:Reference

Use the provided storyboard as the exact visual guide for composition, framing,
character appearance, environment, and sequence progression. <Picture 1> carries
identity, wardrobe, and proportions for both characters — direct only motion,
acting beats, camera, lighting, and audio.

Identity anchors:
- Rin: lean athletic young man, honey-brown low ponytail, charcoal leather doublet over off-white tunic.
- Bram: broad forge-cook, dark topknot and short beard, brass-rimmed goggles on his forehead.

Environment: rustic stone cookhouse at morning — arched windows, blazing stone
hearth, flour-dusted oak butcher block.

Guardrails: exactly two characters present at all times; no one new enters or
leaves. Hands remain natural with five fingers. No on-screen text, labels, or
logos. The golden dough ribbons stay translucent and crystalline; no melting
into shapeless blobs. No style drift mid-shot.

Core creative concept: two friends turn a magical golden dough into crackling
crystalline noodles and share the moment of mastery.

Generate a cinematic 15.0-second sequence matching the 6-panel storyboard.
Hand-crafted storybook fantasy illustration with gouache texture and warm
painted brushwork. Warm amber lantern light with orange hearth rim light.
Expressive limited-animation accents with clear poses and readable silhouettes.
Feature-film quality. Expressive facial acting. Temporal consistency.

Timeline
```

*(Shots follow on the next section.)*

```
SHOT 1 — 0.0–4.0s (Continuous Shot)

A medium two-shot on the flour-dusted prep table. Rin kneads the glowing golden
dough in rhythmic folds on screen-left; at the second second Bram sets a spice
tray down on screen-right and leans in to watch. Rin's hands press, fold, and
press again as flour dust drifts through the lantern light.
The camera holds a static eye-level framing of the table with small amplitude at slow speed.
Audio:
- diegetic_dialogue: None
- foley_and_sfx: Rhythmic wooden thuds of dough on oak, soft rustle of flour dust.
- environmental_ambience: Distant crackle of the stone hearth embers.
- non_diegetic_music: Warm acoustic folk guitar, gentle tempo, building slightly.
Cut on the action.

SHOT 2 — 4.0–7.5s (Continuous Shot)

A wide shot across the butcher block. Rin draws the heavy rolling pin outward in
long even strokes; by the second second the dough flattens into a paper-thin
translucent golden sheet, and chili and salt crystals glint inside as it settles.
The camera tracks across the table from left to right with small amplitude at slow speed.
Audio:
- diegetic_dialogue: None
- foley_and_sfx: Low resonant rumble of the rolling pin on timber, delicate crystalline tinkling.
- environmental_ambience: Cookhouse room tone, soft fire hush.
- non_diegetic_music: The folk guitar holds a steady warm rhythm.
Cut on the action.

SHOT 3 — 7.5–11.5s (Continuous Shot)

A tight closeup on Rin's gloved hands. He draws the curved cleaver swiftly across
the sheet; each golden ribbon separates with a harmless orange spark and a sharp
musical snap, and Bram's goggled brow leans into frame with wide, amazed eyes.
The camera pushes in toward the blade with small amplitude at medium speed.
Audio:
- diegetic_dialogue: None
- foley_and_sfx: Crisp rhythmic slicing, tiny popping sparks, sharp candy-like snaps.
- environmental_ambience: Cookhouse room tone.
- non_diegetic_music: The guitar brightens with a rising, delighted lilt.
Cut to the reaction.

SHOT 4 — 11.5–15.0s (Continuous Shot)

A medium symmetrical two-shot. Rin lifts a cascade of rippled golden ribbons high
between his outstretched hands; at the second second they coil and crackle with
red spice dust, and Bram grins broadly and nods toward the roaring hearth as the
pair settle into shared pride.
The camera pulls back to widen onto both friends with medium amplitude at slow speed.
Audio:
- diegetic_dialogue: None
- foley_and_sfx: Shimmering rattle of rigid coiled noodles, Bram's booming chuckle.
- environmental_ambience: Warm hearth crackle filling the room.
- non_diegetic_music: The guitar swells into a warm, satisfying resolve.
```

**Why this is better:** identity anchors are ~13 words each (the sheet carries the
rest); every shot has a full 4-layer audio block with score continuity; each camera
commits to one motion; each shot narrates second-by-second; guardrails are specific
to this scene; no panel references; style stays in one family.

