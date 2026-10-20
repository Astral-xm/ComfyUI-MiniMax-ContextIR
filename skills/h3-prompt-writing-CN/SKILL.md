---
name: h3-prompt-writing-CN
description: Write MiniMax H3 video generation prompts for T2VA, I2VA, FL2VA, L2VA, and Ref2VA with a Simplified-Chinese descriptive body. Keep all fixed H3 field names, section headers, reference labels, timing notation, camera vocabulary, retention keys, and official instruction lines in English.
---

# H3 Prompt Writing (Chinese Body)

## Language Policy (mandatory)

The final optimized prompt is a mixed-language H3 prompt. It is not a fully translated Chinese prompt.

### Write the descriptive body in Simplified Chinese

- `integrated_multimodal_description` / `detailed_description`: write the prose in Chinese, including visual style, composition, subject appearance and position, environment, props, actions, reactions, lighting, physics/VFX, continuity, and diegetic sound.
- `subject_definitions`, `summary`, and `retention_analysis`: write the explanatory prose in Chinese.
- `overall_soundscape` and `non_diegetic_music`: write the descriptive sentences in Chinese.
- Keep the Chinese natural, specific, and production-ready. Do not write an English draft and translate it mechanically.

### Keep the following in English exactly as specified

- Field names and section headers: `integrated_multimodal_description:`, `overall_soundscape:`, `non_diegetic_music:`, `subject_definitions:`, `summary:`, `retention_analysis:`, `detailed_description:`.
- Reference labels and tags: `<Subject N>`, `<Picture N>`, `<Video N>`, `<Audio N>`, `<Image N>`, `<d>...</d>`, `<scenetrans>`, and `<cutoff>`.
- Shot markers and timing notation: `[Shot 1]`, `00:03.000`, `0.00 seconds`, `S.SS-second mark`.
- Task-type prefixes in `summary`, such as `[reference generation]`, `[video editing + audio reuse]`, and `[keyframe completion]`; keep the square brackets and English type names.
- The official I2VA / FL2VA / L2VA instruction lines (the "For the target video..." and "How the reference pictures align..." lines), verbatim.
- Fixed style descriptors and camera/lighting/material/VFX vocabulary, for example `Cinematic`, `live-action`, `2D-animated`, `3D CG`, `claymation`, `watercolor`, `vintage film`, `Static Shot`, `tracking shot`, `push-in`, `pull-back`, `pan`, `tilt`, `orbit / arc`, `swoop`, `whip-pan`, `dive / plunge`, `Truck Left / Truck Right`, `Roll Clockwise / Roll Counterclockwise`, `with small amplitude`, `with large amplitude`, `at slow speed`, `at fast speed`, `close-up`, `medium shot`, `wide shot`.
- Retention relationship keys: `fully_preserved`, `partially_preserved`, `attribute_transfer`, `weak_reference`, `newly_generated`, `fully_copy`, `partially_copy`, `reference`.
- Speaker IDs such as `(S1)`, audio language tags such as `[Chinese]` / `[English]`, and `N/A`.

Do not translate fixed tokens. Embed them naturally in the Chinese sentence.

### Example of the required mixed format

```text
integrated_multimodal_description: [Shot 1] Cinematic, live-action，中景 Static Shot 建立明亮的出租屋日景。年轻女性（S1）坐在木桌前，... 镜头缓慢 push-in，...

overall_soundscape: 安静的室内环境声，...

non_diegetic_music: N/A
```

Full-reference example:

```text
subject_definitions:
<Subject 1> 是 <Picture 1> 中的年轻女性，长黑发，穿浅蓝色衬衫，...

summary:
[reference generation] 一名年轻女性在出租屋内发现手机上的招聘消息，从紧张转为兴奋，...

retention_analysis:
<Subject 1> — fully_preserved：面部、发型、服装和体型保持...

detailed_description:
[Shot 1] Cinematic, live-action，中景 Static Shot...

overall_soundscape: ...

non_diegetic_music: N/A
```

Dialogue, lyrics, and visible on-screen text inside `<d>...</d>` or quotation marks must keep their original language and exact wording. Do not translate them unless the user explicitly asks for a translated performance.

If the user explicitly requests a different body language, follow that request for the descriptive body only. All fixed H3 tokens above remain English.

## Workflow

1. Identify the input mode: T2VA, I2VA, FL2VA, L2VA, or full-reference Ref2VA.
2. For base text/keyframe modes, read `references/base-en.txt` and follow its final prompt structure.
3. For full-reference mode, read `references/ref-en.txt` and follow its six-section rewrite format.
4. Preserve the exact field names, section order, labels, timing notation, camera vocabulary, and official instruction lines from the selected guide. Write the descriptive body in Simplified Chinese per the Language Policy.

## Base Modes

- T2VA: build the full audiovisual timeline from text.
- I2VA: start from the first frame and develop forward from it.
- FL2VA: describe the continuous path between the first and last frames.
- L2VA: infer a plausible opening and converge to the supplied last frame.

Use `integrated_multimodal_description`, `overall_soundscape`, and `non_diegetic_music` in the order shown in `references/base-en.txt`.

## Full-Reference Mode

Ref2VA rewrites use `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, and `non_diegetic_music` in that order. Reference labels stay consistent across all sections.

Read `references/ref-en.txt` for label rules, retention analysis, and complete examples.

## Output Rules

- Write the descriptive body in Simplified Chinese; keep all fixed H3 field names, labels, timing notation, camera vocabulary, retention keys, speaker IDs, audio language tags, and official instruction lines in English.
- Preserve dialogue, lyrics, and visible scene text in their original language and exact wording.
- Describe each shot by composition, subjects, environment, actions, camera, sound, and the exact point where referenced content appears.
- If a picture or video only defines a Subject's appearance, do not add a standalone line for it in `retention_analysis`; cite it inside the Subject definition and record the Subject's retention. `attribute_transfer` is only for attributes transferred to a different target.
- Avoid plot summaries, unresolved reference labels, and timing that does not match the requested duration.
- Output only the final H3 prompt. Do not add a separate English version, a Chinese explanation, or translation notes.
