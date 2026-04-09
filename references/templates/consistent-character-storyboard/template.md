---
id: consistent-character-storyboard
type: workflow
title: 角色一致性分镜工作流
title_en: Consistent Character Storyboard Workflow
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: general
tags: [分镜, 角色一致性, 故事板, storyboard, contact-sheet, multi-shot]
models:
  - name: gemini-3.1-flash-image-preview
    tested: false
    quality: good
  - name: gemini-3-pro-image-preview
    tested: false
    quality: expected-best
aspect: "1:1"
difficulty: intermediate
samples:
  - file: samples/sample-3-pro-01.png
    model: gemini-3-pro-image-preview
    prompt: "Using the provided reference image of Miso, create a 3x3 contact sheet. All 9 cells must show the same Siamese cat character, the same teal neck scarf with a small gold bell, the same soft pastel interior environment, and the same warm daylight lighting. Each cell should use a different natural pose or camera angle while keeping facial structure, fur pattern, blue eyes, proportions, palette, and background continuity stable across the grid. Avoid duplicate frames. Keep the tone cute, clean, and IP-friendly."
    aspect: "1:1"
created: 2026-03-31
updated: 2026-03-31
---

## Goal

Guide the agent through a repeatable storyboard exploration workflow: first lock a master character reference, then explore multi-shot boards, then iterate with single-variable edits so the character stays consistent across frames without overcommitting too early to a final story layout.

## When To Use

- AI short drama or manga storyboard exploration before final production
- Same character across multiple camera angles, poses, or emotional beats
- Character design extension from one approved master frame
- Multi-panel story beats where continuity matters more than single-image spectacle
- Teams that want a low-risk loop: lock identity first, then widen the shot language gradually

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `subject_name` | recommended | Stable character name used in every prompt, for example `Aki` or `Captain Eva` |
| `master_reference` | recommended | One approved image that locks face, hair, outfit, palette, and lighting direction; if missing, the workflow must create it first |
| `reference_pack` | optional | Two to three supporting images used only when they reinforce consistency instead of introducing drift |
| `style_lock` | optional | Realistic, manga, cinematic still, watercolor, and so on |
| `continuity_locks` | recommended | The elements that must stay stable: face shape, hairstyle, outfit, palette, background direction, lighting logic |
| `board_mode` | recommended | `3x3 contact sheet` for angle exploration or `9-panel storyboard` for scene exploration |
| `story_beats` | optional | The intended beats, such as calm opening, tense close-up, action beat, quiet ending |
| `iteration_target` | optional | The one variable to change next: expression, camera angle, pose, framing density, or shot distance |
| `stop_condition` | optional | For example: one approved master frame, one usable contact sheet, or one coherent 9-panel exploration board |

## Steps

1. Determine the entry mode. If the user already has an approved character image, start from it. If not, create a single master reference first and do not move to storyboard generation until identity is accepted.
2. Lock the character name and continuity checklist. Reuse the exact same `subject_name` in every later prompt. Do not alternate between aliases once the workflow starts.
3. Choose the exploration target before generating: use `3x3 contact sheet` when the goal is angle and pose range; use `9-panel storyboard` only after the master identity is stable enough to carry a continuous scene.
4. Generate the first board from the master reference. If additional support images exist, use at most two or three that reinforce the same identity. Do not introduce unrelated references that can confuse the subject.
5. Review the result in this order: identity continuity, outfit continuity, environment logic, lighting continuity, then shot diversity. Reject boards that look varied but lose identity.
6. If drift is mild, run a repair pass that restates the locked invariants. If drift is severe, fall back to the last approved reference and regenerate instead of stacking more corrections on a broken board.
7. Iterate one major variable at a time. Good deltas are expression, camera position, pose, motion beat, framing density, or shot distance. Do not change character identity, scene, lighting, and style in the same round.
8. Promote good outputs forward. When one panel or one board is clearly the current best state, save it as the new working reference for the next round. Prefer editing from the last accepted state instead of rewriting the entire prompt from scratch.
9. Stop as soon as the current `stop_condition` is satisfied. This workflow is for exploration, so it should preserve optionality instead of forcing full production lock-in too early.

## Prompt Blocks

### Master Reference Prompt

```text
Create an image of a {{subject_name|female character named Aki}}. She has {{identity_lock|a short black bob haircut, sharp eyes, pale skin, and a calm expression}}. She is wearing {{outfit_lock|a dark tailored coat, silver earrings, and black leather gloves}}. The scene uses {{scene_lock|a dim cinematic interior with warm side lighting and a deep red-black background}}. Keep the composition clean and consistent. This image will serve as the master reference for later storyboard shots.
```

### Contact Sheet Prompt

```text
Using the provided reference image of {{subject_name|Aki}}, create a 3x3 contact sheet. All 9 cells must show the same character, the same outfit, the same environment, and the same lighting. Each cell should use a different natural pose or camera angle while keeping facial structure, hairstyle, palette, proportions, and background continuity stable across the grid. Avoid duplicate frames.
```

### Storyboard Prompt

```text
Using the provided reference image of {{subject_name|Aki}}, create a 9-panel cinematic storyboard for one continuous scene. Maintain the same character identity, clothing, environment logic, and color palette throughout. The sequence should progress through {{story_beats|a calm opening shot, a tense mid-scene close-up, an action beat, and a quiet final frame}}. No text inside the frames.
```

### Single-Variable Edit Prompt

```text
Keep everything the same. Only change {{iteration_target|her expression to slightly more serious}}. Do not change the face shape, hairstyle, outfit, background, lighting, or overall style.
```

### Continuity Repair Prompt

```text
Using the approved reference image of {{subject_name|Aki}}, repair continuity drift in the current result. Keep the same face shape, hairstyle, outfit, palette, environment direction, and lighting logic. Only correct the identity consistency and do not introduce a new pose, new style, or new background concept.
```

### Shot Planning Prompt

```text
Plan a compact storyboard exploration for {{subject_name|Aki}}. Keep identity, outfit, palette, and setting stable. Propose {{board_mode|a 3x3 contact sheet}} focused on {{exploration_goal|camera angle range, pose variety, and emotional progression}}. The plan should avoid drastic scene changes and should move only one storytelling variable at a time.
```

## Success Checks

- The same character is recognizable in every frame without re-reading a long appearance description
- Outfit, palette, environment logic, and lighting remain stable unless explicitly changed
- The board shows real shot variation without duplicated framing
- Every accepted iteration changes exactly one major variable
- A failed round can fall back cleanly to the last approved reference
- The workflow can stop after any approved step and resume later from the last accepted reference
