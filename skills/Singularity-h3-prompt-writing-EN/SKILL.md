---
name: Singularity-h3-prompt-writing-EN
description: MiniMax H3 Singularity full-reference video prompt writing guide for action, camera, VFX, lighting, sound, and continuity. Write the complete optimized prompt in English while preserving all fixed H3 field names, reference labels, timing notation, camera/VFX vocabulary, retention keys, and instruction tokens exactly.
---

# MiniMax H3 Singularity Video Prompt Writing Specification

Full-Reference Image-to-Video · Enhanced Guide for Action, Camera, VFX, Lighting, Sound, and Continuity
Purpose: This document consolidates the Full-Reference prompt structure and the recurring high-value patterns found in the provided MiniMax training-prompt corpus. It is an engineering-oriented writing guide, not a claim about undocumented internal MiniMax rules.

## 0. Output Language Policy (mandatory)

Write the complete optimized H3 prompt in English. Use natural, production-ready English prose for every descriptive field.

### Write in English

- The descriptive prose in `subject_definitions`, `summary`, `retention_analysis`, and `detailed_description`: identity, appearance, environment, action, camera intent, physics/VFX, lighting, continuity, sound, and dialogue context.
- The descriptive sentences in `overall_soundscape` and `non_diegetic_music`.

### Keep the fixed H3 tokens exactly as specified

- Field names and section headers: `subject_definitions:`, `summary:`, `retention_analysis:`, `detailed_description:`, `overall_soundscape:`, `non_diegetic_music:`.
- Fixed header token: `id="x..."` when the output format includes it.
- Reference labels and tags: `<Subject N>`, `<Environment>`, `<Prop or VFX>`, `<Picture N>`, `<Video N>`, `<Audio N>`, `<Image N>`, and `<d>...</d>`.
- Shot markers and timing notation: `[Shot 1]`, `00:03.000`, `0.00 seconds`, `S.SS-second mark`.
- Task-type prefixes in `summary`, such as `[reference generation]`, `[video editing + audio reuse]`, and `[keyframe completion]`.
- Fixed style descriptors and camera/lighting/material/VFX vocabulary: `Cinematic`, `live-action`, `Static Shot`, `tracking shot`, `push-in`, `pull-back`, `pan`, `tilt`, `orbit`, `arc`, `swoop`, `whip-pan`, `barrel roll`, `Truck Left / Truck Right`, `Roll Clockwise / Roll Counterclockwise`, `with small amplitude`, `with large amplitude`, `at slow speed`, `at fast speed`, `close-up`, `medium shot`, `wide shot`, etc.
- Retention relationship keys: `fully_preserved`, `partially_preserved`, `attribute_transfer`, `weak_reference`, `newly_generated`, `fully_copy`, `partially_copy`, `reference`.
- Speaker IDs such as `(S1)`, audio language tags such as `[Chinese]` / `[English]`, and `N/A`.
- Dialogue, lyrics, and visible on-screen text keep their original language and exact wording.

Example of the required English format:

```text
subject_definitions:
<Subject 1> is the young woman in <Picture 1>, with long dark hair and a light-blue shirt...

summary:
[reference generation] A young woman in a rental apartment discovers a recruitment message on her phone and shifts from tension to excitement...

retention_analysis:
<Subject 1> — fully_preserved: face, hairstyle, clothing, and body shape remain...

detailed_description:
[Shot 1] Cinematic, live-action, a medium Static Shot establishes a bright rental apartment interior...

overall_soundscape: Quiet indoor room ambience...

non_diegetic_music: N/A
```

Output only the final English H3 prompt. Do not add a Chinese translation, a second bilingual version, or translation notes.

## 1. Core Design Principles

A strong H3 prompt should explicitly control the following layers:

* Reference — what visual information is inherited from each reference image.
* Composition — framing, shot size, subject placement, foreground/background relationships.
* Action — continuous, physically readable action rather than isolated action labels.
* Camera — position, movement type, direction, speed, amplitude, and what the camera follows.
* Physics / VFX — particles, impact, recoil, debris, cloth/hair response, smoke, light interaction, and other consequences.
* Lighting / Materials — light source, direction, exposure, reflections, surface response, atmosphere, and depth.
* Audio — ambient sound, synchronized effects, dialogue, and music.
* Continuity — identity, spatial direction, object state, damage state, and temporal progression.

```text
Shot ≈ current composition + subject state + action chain + camera movement + environmental/physical feedback + lighting change + sound/dialogue
Action chain ≈ initial state → trigger → primary action → displacement/momentum → contact or reaction → final state
Camera chain ≈ camera position → movement direction → speed → amplitude → subject followed → focus/depth-of-field result
```

## 2. Standard Full-Reference Prompt Structure

```text
id="x..."
subject_definitions:
...
summary:
...
retention_analysis:
...
detailed_description:
...
overall_soundscape:
...
non_diegetic_music:
...
```

The exact field names above should remain stable when the workflow or application expects this structure.

## 3. subject_definitions

Use subject definitions to establish persistent identity, appearance, environment, props, and other reference-grounded elements.

* Define characters with stable visual identity: face, hair, clothing, body characteristics, and distinctive features.
* Define environments with architecture, terrain, major objects, atmosphere, and visual style.
* Define important props or VFX elements when they need stable visual identity.
* Do not place long time-axis actions here. Put evolving actions in detailed_description.
* If a reference image only defines a character, scene, style, or appearance, connect it to the relevant Subject instead of treating it as an independent video keyframe, and do not add a separate `<Picture N>` line in `retention_analysis`.

## 4. Reference Images: Critical Distinction

A reference image is not automatically a video character or a first frame. Distinguish between visual inheritance and temporal anchoring.

* Use <Subject N> for the actual entity or scene content that should appear in the generated video.
* Use <Picture N> as a standalone reference when it genuinely functions as a first frame, keyframe, last frame, or composition anchor.
* If a picture only supplies appearance, identity, clothing, environment, or style, place that relationship inside the Subject definition.
* State clearly when reference-grounded content becomes active if the reference is intended to affect only part of the sequence.

## 5. summary

Summarize the main visual action and its progression. A useful summary describes what happens, how it develops, and the resulting state—not merely the plot premise.

## 6. retention_analysis

Use retention relationships consistently when the format requires them:

* fully_preserved — the referenced element remains substantially unchanged.
* partially_preserved — only selected properties are retained.
* attribute_transfer — selected visual attributes are transferred to another generated element.
* weak_reference — the reference provides loose visual guidance.
* newly_generated — the element is created without meaningful reference inheritance.
* For audio: fully_copy, partially_copy, reference, weak_reference.

A `<Picture N>` or `<Video N>` line is valid in `retention_analysis` only when that asset is a separate referenced item (a concrete frame/keyframe, a source video for editing/continuation, or a storyboard/structural reference). If it only supplies appearance, identity, clothing, environment, or style for a `<Subject N>`, cite it inside the Subject definition and record only the Subject's retention. Do not use `attribute_transfer` for a source that merely defines the Subject's own appearance.

Correct:

```text
<Subject 1> (appears in [Shot 1]): fully_preserved - ...
<Picture 1> ([Shot 1] first frame): fully_preserved - ...
```

Wrong:

```text
<Picture 2>: attribute_transfer - appearance source for <Subject 1>...
```

In hybrid mode (keyframes + reference images), keyframe pictures (first frame, last frame, or another concrete keyframe) still get their own `fully_preserved` lines. A reference image used only as a Subject's appearance source remains a source citation inside the Subject definition, even if that Subject also appears in a keyframe; it does not get a separate retention line.

## 7. detailed_description — The Core Field

Organize the description shot-by-shot in playback order. Each shot should answer seven practical questions: what is visible, where the subject is, what state it starts in, what it continuously does, how the camera moves, what visual/physical feedback occurs, and what is heard.

```text
[Shot 1] [shot size / camera position] establishes [subject position + composition].
[Subject] begins in [initial state], then [trigger/action initiation].
As [primary action] continues, [body movement / displacement / prop movement].
The camera [movement] at [speed/amplitude], keeping [subject] in [composition relationship].
At the moment of [contact / impact / emotional change], [VFX / physical response / lighting change] occurs.
The shot ends with [final pose / final state], while [sound/dialogue] continues or resolves.
```

For later shots, use explicit timestamps such as:

```text
[Shot 2] At 00:03.000, ...
```

Shot 1 has no timestamp in the recommended structure; later shots should use timestamps when temporal precision matters.

## 8. Action Writing: From Labels to Processes

Avoid isolated verbs such as “walks,” “attacks,” “turns,” or “explodes” when the action needs to be visually reliable. Expand them into a causal sequence.

```text
Preparation → Trigger → Acceleration → Primary action → Contact → Reaction → Recovery → Final state
```

**Weak:**

```text
The warrior attacks the enemy.
```

**Stronger:**

```text
The warrior lowers his center of gravity, shifts one foot forward, draws the sword back, then accelerates into a forward slash. The blade cuts across the frame with visible momentum; the opponent recoils from the impact, while loose fabric and dust react to the movement. The warrior completes the follow-through and settles into a guarded stance.
```

For distant characters, explicitly preserve continuous movement:
The two distant characters continue walking throughout the shot at a steady pace; their steps remain continuous even though their small scale makes the movement visually subtle.

## 9. Camera / Cinematography

Avoid vague phrases such as “dynamic camera” or “cinematic camera.” Specify the camera behavior.

* Tracking shot — follows a moving subject along a defined path.
* Push-in — camera moves toward the subject, increasing visual emphasis.
* Pull-back — camera retreats to reveal space or reduce emphasis.
* Pan — camera rotates horizontally.
* Tilt — camera rotates vertically.
* Orbit / arc — camera moves around the subject while maintaining a spatial relationship.
* Swoop — camera travels through space with a pronounced curved or diving trajectory.
* Whip-pan — rapid directional rotation, useful for transitions or sudden changes.
* Dive / plunge — camera moves sharply downward or forward from an elevated viewpoint.
* Barrel roll — camera rotates around the lens axis while moving through space.
* Handheld — controlled small-scale camera shake suggesting physical presence or instability.
* Static / locked-off — camera remains fixed while the action unfolds.
A robust camera specification contains five elements:
camera position / shot size + movement + direction + speed / amplitude + subject to follow
Bind the camera to the action. For example, a side-tracking camera can maintain a character in profile while matching the character's running speed; a push-in can accelerate toward the instant of impact.

## 10. VFX and Physical Feedback

Do not write only “add cool effects.” Describe the trigger, visual form, motion, and environmental consequence.

```text
VFX ≈ trigger condition + form + direction/motion + interaction with environment/subjects
```

* Energy / magic — describe emission point, shape, direction, intensity, travel path, and impact.
* Explosion — specify the ignition/impact point, expanding fire/smoke, debris trajectory, pressure wave, and environmental response.
* Sparks — specify source, density, direction, brightness, and decay.
* Smoke / dust — specify origin, expansion, drift, turbulence, and interaction with light.
* Fragments — specify what breaks, fragment direction, scale, and momentum.
* Liquid / blood — specify the impact source, spray direction, droplets, and subsequent settling.
* Rifts / portals — specify formation, edge behavior, internal motion, emission, and disappearance.
* Lightning — specify origin, branching, flash timing, illumination, and contact effect.
Always consider physical feedback: hair and clothing react to force, weapons recoil, dust rises from footsteps, ice cracks under pressure, nearby surfaces receive light from explosions, and particles inherit momentum from impacts.

## 11. Lighting, Materials, and Visual Texture

Replace generic quality language with concrete visual controls.

* Light source and direction.
* Warm/cool or otherwise specified light characteristics when important.
* Exposure and contrast changes.
* Reflections and wet-surface response.
* Volumetric light, haze, smoke, or atmospheric depth.
* Depth of field and focus transitions.
* Motion blur only when justified by rapid motion.
* Material response: skin, metal, fabric, glass, water, ice, stone, etc.
Words such as “cinematic,” “epic,” “high quality,” and “dynamic” can support a description, but should never replace observable visual instructions.

## 12. Multi-Shot Timeline and Continuity

Write shots in playback order and preserve causal continuity.

* Maintain consistent screen direction unless a deliberate reversal is specified.
* Track weapon position, body pose, object ownership, and prop state between shots.
* Carry damage, dirt, blood, smoke, broken objects, and other persistent states forward when appropriate.
* Maintain consistent character identity and clothing.
* Preserve the intended reference-image anchor when a picture is used as a keyframe.
* Synchronize sound effects with visible impacts and actions.
* Use timestamps for later shots when precise timing matters.

## 13. Character Acting and Emotion

Convert abstract emotions into observable micro-actions.

* Eyes: gaze direction, blinking, widening, narrowing, tracking.
* Face: eyebrow movement, lip tension, jaw movement, smile/frown changes.
* Breathing: chest or shoulder movement, visible recovery after exertion.
* Posture: shoulders, spine, head angle, center of gravity.
* Hands: grip tension, finger movement, hesitation, release.
* Attention: explicitly state what the character looks at or reacts to.
Instead of only saying “she looks nervous,” describe the behavior: her gaze shifts toward the doorway, her lips tighten, her breathing becomes shallow, and her fingers repeatedly adjust their grip.

## 14. Dialogue, Soundscape, and Music

Keep speaker identities stable across shots.

```text
(S1) speaks: "..."
(S2) replies: "..."
```

* Use stable speaker IDs such as (S1), (S2), etc.
* Synchronize dialogue with visible mouth movement when the format requires it.
* Place important diegetic effects in the overall_soundscape.
* Use non_diegetic_music for background score rather than mixing it with physical scene sounds.
* Synchronize footsteps, impacts, weapon clashes, explosions, wind, water, and other effects with visible events.

## 15. Reusable High-Value Templates

### 15.1 Distant Continuous Walking

```text
[Shot 1] A wide establishing shot shows <Subject 1> and <Subject 2> far in the background.
Both subjects continue walking steadily along the path throughout the entire shot, maintaining consistent direction and spacing.
The camera performs a slow lateral tracking movement, keeping the distant figures within the wide composition.
Their clothing and hair move subtly with the surrounding breeze, while the environment remains visually dominant.
```

### 15.2 Wuxia / Xianxia Combat

```text
[Shot 1] A medium-wide side angle frames <Subject 1> and <Subject 2> in opposing positions.
<Subject 1> shifts into a lower stance, draws the weapon backward, then launches forward with accelerating momentum.
The camera tracks laterally with the attack, then arcs around the point of contact.
At impact, sparks and dust burst outward, the opponent recoils, clothing and hair react to the force, and loose debris is displaced across the ground.
The attacker completes the follow-through and settles into a controlled stance.
```

### 15.3 Explosion / Disaster

```text
[Shot 1] The camera begins in a stable wide shot as <Subject 1> stands near the center of the environment.
A sudden trigger occurs behind the subject, followed by a rapidly expanding explosion.
The camera pulls backward while panning to keep the subject and blast inside the frame.
Fire, smoke, debris, dust, and fragments expand outward; nearby surfaces are illuminated by the flash and respond to the pressure wave.
The shot ends as the initial blast subsides into drifting smoke and falling debris.
```

### 15.4 Magic / Energy Effect

```text
[Shot 1] <Subject 1> raises one hand and gathers a concentrated energy field around the palm.
The energy intensifies from a small glow into a dense rotating mass, with particles spiraling inward before being released forward.
The camera pushes toward the hand, then tracks the energy projectile as it travels through the environment.
At impact, a shockwave expands outward, nearby dust and loose objects are displaced, and the surrounding surfaces receive a brief burst of colored illumination.
```

## 16. Common Failure Modes

* Using only generic descriptors such as cinematic, dynamic, epic, or high-definition.
* Treating every reference image as an automatic first frame.
* Using one-word actions instead of continuous action chains.
* Writing “dynamic camera” without movement type, direction, speed, or subject relationship.
* Writing “cool VFX” without trigger, form, motion, or physical consequence.
* Applying heavy motion blur to every movement.
* Packing too many simultaneous actions into one shot.
* Redefining the same Subject inconsistently across shots.
* Failing to synchronize sound with visible events.
* Describing emotions abstractly without observable acting.
* Failing to state continuous walking when distant characters are intended to keep walking.

## 17. Final Quality Checklist

* Is every important reference image clearly assigned a purpose?
* Are Subject identities stable?
* Does every major action have a beginning, progression, reaction, and ending state?
* Is camera movement concrete and connected to the action?
* Are VFX tied to physical triggers and consequences?
* Are lighting and material changes observable rather than generic?
* Are sounds synchronized with visible events?
* Are speaker IDs stable?
* Is continuity preserved between shots?
* Are distant/background actions explicitly described when they must continue?
* Have unnecessary generic adjectives been replaced with concrete visual information?

## 18. Copyable Master Template

```text
id="x..."

subject_definitions:
<Subject 1>: [identity / appearance / clothing / distinctive features / reference relationship]
<Subject 2>: [identity / appearance / clothing / distinctive features / reference relationship]
<Environment>: [location / architecture / terrain / atmosphere / lighting]
<Prop or VFX>: [appearance / material / persistent characteristics]

summary:
[Main action progression and final state]

retention_analysis:
[Reference → Subject relationships and preservation level]

detailed_description:
[Shot 1] [shot size / camera position] establishes [composition].
[Subject] begins in [initial state], then [trigger].
As [primary action] continues, [body / prop / environmental movement].
The camera [movement] toward / along / around [direction], at [speed / amplitude], following [subject].
At [impact / contact / emotional beat], [VFX / physics / lighting response].
The shot ends with [final state].

[Shot 2] At 00:03.000, [new composition and continuing state].
[Action progression + camera + physical response + sound].
[Continue as needed.]

overall_soundscape:
[Ambient environment + synchronized diegetic effects + dialogue]

non_diegetic_music:
[Music style / intensity / progression, if applicable]
```

> **Language note:** Keep the field names, labels, shot markers, timestamps, retention keys, and fixed camera/VFX vocabulary in English. Replace the bracketed placeholders with English descriptive content.

## 19. Single-Shot High-Quality Example

```text
[Shot 1] A low-angle medium-wide tracking shot frames the warrior in the foreground, with the opponent several meters ahead on the same axis.
The warrior begins in a compressed defensive stance, shoulders lowered and sword held close to the body. He shifts his rear foot forward, rotates his hips, draws the blade backward, and suddenly accelerates into a forward charge.
The camera tracks backward at matching speed, maintaining the warrior in the lower-center of the frame while preserving the opponent in the background.
As the warrior closes the distance, the blade swings upward and transitions into a diagonal slash. At the instant of contact, bright sparks burst from the collision point, dust lifts from the ground, and both characters' clothing and hair react to the force.
The opponent is pushed backward several steps, briefly loses balance, then regains footing. The warrior completes the follow-through and lowers the blade into a guarded stance.
The camera performs a small arc around the contact point and settles into a wider composition as the dust begins to disperse.
Footsteps, cloth movement, the metallic impact, and drifting environmental ambience remain synchronized with the visible action.
```

The example is intentionally concrete: it specifies starting state, action progression, camera behavior, physical response, final state, and synchronized sound instead of relying on generic quality adjectives.

> **Language note:** The example above shows the target English output style and level of detail. Write the final H3 prompt in English while keeping `[Shot 1]`, `Static Shot`, camera terms, and all other fixed tokens exactly as specified.

## 20. Training-Corpus-Derived High-Value Patterns

The following patterns are especially useful because they repeatedly improve action readability and visual specificity in the provided training material:

* Use explicit camera verbs: track, push in, pull back, pan, tilt, orbit, arc, swoop, dive, whip-pan, barrel roll.
* Use action verbs that imply visible mechanics: shift weight, brace, draw back, accelerate, lunge, swing through, recoil, stagger, recover, settle.
* Describe environmental response: dust, sparks, fragments, smoke, cloth, hair, reflections, debris, pressure waves.
* Connect cause and effect: trigger → movement → impact → reaction.
* Use temporal transitions: initially, then, as the action continues, at the moment of impact, afterward, finally.
* Keep the camera and action synchronized rather than describing them as unrelated lists.
* Use concrete lighting and material behavior instead of generic quality claims.
These are corpus-derived writing patterns. They should be treated as practical prompt-engineering guidance rather than undocumented official MiniMax implementation rules.

## 21. Recommended Prompt-Building Workflow

1. Define the reference relationship first: what is inherited and what is newly generated.
2. Lock the persistent Subject and Environment descriptions.
3. Write the composition and starting state of each shot.
4. Expand the main action into a continuous causal chain.
5. Add camera movement that physically follows or emphasizes the action.
6. Add VFX and environmental reactions at the exact trigger points.
7. Add lighting/material changes that result from the event.
8. Add synchronized sound and dialogue.
9. Check continuity across the timeline.
10. Remove vague filler and replace it with observable details.

## 22. Output Language Checklist

- [ ] All field names and section headers use the exact English tokens.
- [ ] All reference labels, `[Shot N]`, timestamps, retention keys, speaker IDs, and audio tags remain English.
- [ ] Camera/VFX vocabulary uses the fixed English vocabulary from this guide.
- [ ] The entire descriptive body is natural English.
- [ ] Dialogue, lyrics, and visible text preserve their original language and exact wording.
- [ ] No standalone `<Picture N>` / `<Video N>` retention line for an asset that only defines a Subject's appearance.
- [ ] `attribute_transfer` is used only for attributes transferred to a different target, not for a Subject's own appearance source.
- [ ] The output contains no translation notes or duplicate/bilingual versions.
