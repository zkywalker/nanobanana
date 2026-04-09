---
id: asset-style-consistency-pack
type: workflow
title: 本地素材风格统一工作流
title_en: Local Asset Style Consistency Workflow
description: 基于本地输入图、参考图和锁定约束，先做一个统一风格样张，再稳定地扩展成一组风格一致的素材。
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: general
tags: [素材包, 风格统一, 多图一致性, reference, batch, consistency, edit]
models:
  - name: gemini-3-pro-image-preview
    tested: true
    quality: best
  - name: gemini-3.1-flash-image-preview
    tested: false
    quality: good
aspect: "1:1"
difficulty: advanced
category: assets
samples:
  - file: samples/sample-3-pro-01.png
    model: gemini-3-pro-image-preview
    prompt: "Keep the exact building layout, pool placement, fountain placement, trees, and overall camera angle unchanged. Transform this image into a clean architectural concept illustration with a restrained pastel palette, soft afternoon lighting, matte materials, and crisp presentation lines. Preserve the house geometry and outdoor elements while normalizing the whole scene into one polished visual family. Do not add new objects or change the composition."
    aspect: "16:9"
  - file: samples/sample-3-pro-02.png
    model: gemini-3-pro-image-preview
    prompt: "Keep the exact building layout, pool placement, fountain placement, trees, and overall camera angle unchanged. Restyle this image into a premium dusk visualization with deep navy shadows, warm interior glow, reflective water, cleaner material separation, and polished architectural presentation. Preserve the house geometry and all outdoor elements while shifting the whole image into one coherent evening-render family. Do not add new objects or change the composition."
    aspect: "16:9"
created: 2026-03-31
updated: 2026-03-31
---

## Goal

Guide the agent through creating a consistent asset pack from local images: first lock one approved style anchor, then propagate the same style and constraints across additional assets without letting color, composition logic, or character identity drift.

## When To Use

- A team has several local source images that should look like one set
- Marketing, sticker, icon, or character assets need the same palette and rendering logic
- The user has one strong reference image and several weaker source images
- Editing with `--input` and `--ref` is more appropriate than generating everything from scratch
- Consistency matters more than maximal novelty

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `anchor_image` | recommended | One image that best represents the intended final style |
| `asset_pack` | recommended | The set of local images to normalize or restyle |
| `reference_images` | optional | Up to two or three supporting references that reinforce the same style rather than competing with it |
| `style_lock` | recommended | The non-negotiable style traits: palette, line weight, lighting, material logic, mood |
| `must_keep` | recommended | What must survive editing: logos, silhouettes, text, transparent background, crop, character identity |
| `output_spec` | optional | File naming, target size, aspect ratio, transparent background needs, delivery format |
| `stop_condition` | optional | One approved hero asset, one coherent mini-pack, or a full asset batch |

## Steps

1. Pick the best anchor first. If no single image is strong enough, create one style anchor before batch work starts.
2. Write a short style lock with only the traits that truly matter. Too many vague style notes cause drift instead of consistency.
3. Separate the batch into similar groups if needed. Do not force one edit prompt across assets with different crops or content structure.
4. Run one exemplar edit first using the anchor image plus at most two or three reinforcing references. Lock the must-keep constraints explicitly.
5. Review the exemplar in this order: preserved content, style match, palette stability, then polish. If the exemplar drifts, repair it before touching the rest of the pack.
6. Propagate the approved style to the next assets one at a time or in small clusters. Reuse the same locked style wording and only change the asset-specific constraints.
7. Stop when the batch feels like one family. If one asset refuses to match, treat it as a special case instead of weakening the style lock for every file.

## Prompt Blocks

### Style Anchor Prompt

```text
Using the provided input image and reference images, create one approved style anchor for this asset pack. Keep {{must_keep|the subject identity, core silhouette, and any locked text or logo}} unchanged. Apply {{style_lock|a restrained pastel palette, soft editorial lighting, and clean modern rendering}} consistently. This result should define the visual rules for the rest of the pack.
```

### Consistency Edit Prompt

```text
Using the approved style anchor and the current input image, keep {{must_keep|the original composition, locked logo, and subject identity}} unchanged. Apply the same style rules as the anchor: {{style_lock|the same palette, line weight, lighting logic, and material finish}}. Do not introduce a new background concept or a different mood. Only normalize this asset into the same family.
```

### Drift Repair Prompt

```text
Keep the asset in the same family as the approved anchor. Repair only style drift: bring the palette, contrast, lighting logic, and rendering finish back into alignment while preserving the locked content and composition.
```

## Success Checks

- Every accepted asset still preserves its locked content
- The pack shares one believable palette and rendering logic
- No single asset looks like it came from a different model or art direction
- The process can reuse one approved anchor instead of rewriting style from scratch each time
- A reviewer can describe the pack with one short style sentence
