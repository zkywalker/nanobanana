---
id: readme-launch-visual
type: workflow
title: README 启动视觉工作流
title_en: README Launch Visual Workflow
description: 从 README、定位文案或功能清单里抽出一句主张和一张主视觉，生成适合首页头图、OG 封面或发布海报的图像。
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: text-heavy
tags: [README, 头图, 海报, 封面, OG, launch, hero, banner]
models:
  - name: gemini-3-pro-image-preview
    tested: true
    quality: best
  - name: gemini-3.1-flash-image-preview
    tested: false
    quality: good
aspect: "16:9"
difficulty: intermediate
category: marketing
samples:
  - file: samples/sample-3-pro-01.png
    model: gemini-3-pro-image-preview
    prompt: "Create a launch visual for BananaHub. Use the exact headline 'Agent-native image workflows' as the dominant text. Add the supporting line 'Prompt optimization, templates, and editing in one flow' in a smaller secondary position. The asset target is a homepage hero banner. Use a bold terminal-meets-product-doc composition with layered prompt cards flowing into generated image frames. Keep the design high-contrast, clean, and readable at a glance. Use a modern editorial product aesthetic with warm banana gold, ink black, and paper white. Do not invent extra UI labels or filler marketing copy."
    aspect: "16:9"
  - file: samples/sample-3-pro-02.png
    model: gemini-3-pro-image-preview
    prompt: "Create an OG cover image for BananaHub. Keep the exact headline 'Build image workflows, not prompt piles'. Use minimal supporting text: 'Templates, editing, and iterative guidance for Gemini images'. Composition should be optimized for a wide social card, with clear breathing room around the text and one memorable visual metaphor based on modular prompt cards snapping into a guided workflow. Strong hierarchy, strong contrast, no clutter. Use a clean editorial product aesthetic with banana gold accents, black typography, and subtle paper texture."
    aspect: "16:9"
created: 2026-03-31
updated: 2026-03-31
---

## Goal

Guide the agent through converting README or positioning text into one launch-ready visual with locked copy, a clear headline hierarchy, and a visual metaphor that matches the actual product instead of generic AI poster aesthetics.

## When To Use

- A project has a README but no strong hero image
- The user wants an OG cover, launch banner, homepage hero, or product teaser
- One short message must land clearly without reading the full docs
- The agent can read local copy, feature bullets, or issue notes before generating
- Text hierarchy and product positioning matter more than pure art direction

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `source_copy` | recommended | README headline, tagline, feature bullets, launch note, or local text the agent can read first |
| `asset_target` | recommended | Homepage hero, OG cover, launch poster, social banner, waitlist graphic |
| `product_name` | recommended | Exact product or repo name |
| `headline_lock` | optional | Exact headline text that must appear in the image |
| `supporting_copy` | optional | Subtitle, short feature list, or CTA if it must render in the image |
| `visual_metaphor` | optional | Browser window, terminal collage, layered cards, repo map, mascot, and so on |
| `style_lock` | optional | Minimal, editorial, technical, retro terminal, playful, clean SaaS |

## Steps

1. Read the available README or product copy first. Distill it into one core promise, one supporting proof point, and one visual metaphor before writing any image prompt.
2. Decide whether the image is primarily text-led or visual-led. If the copy is still unstable, fix the copy first instead of prompting around vague text.
3. Lock the exact text hierarchy. Prefer one headline and one short support line. Do not ask Gemini to render a full paragraph.
4. Match the composition to the target asset. OG covers need bold readable text; homepage heroes can tolerate more scene detail; posters can carry a stronger visual metaphor.
5. Generate the first version with conservative copy volume, strong contrast, and one dominant focal point. Avoid piling on many floating UI fragments or fake dashboards.
6. Review the result in this order: text accuracy, hierarchy, brand fit, then polish. If the copy is wrong, shorten or simplify it before trying style tweaks.
7. Iterate one major variable at a time: headline wording, composition, metaphor, palette, or density. Do not change all of them at once.

## Prompt Blocks

### Hero Visual Prompt

```text
Create a launch visual for {{product_name|this product}}. Use the exact headline "{{headline_lock|Agent-native image workflows}}" as the dominant text. Add the supporting line "{{supporting_copy|Prompt optimization, templates, and editing in one flow}}" in a smaller secondary position. The asset target is {{asset_target|a homepage hero banner}}. Use {{visual_metaphor|a bold terminal-meets-product-doc composition with one strong focal object}}. Keep the design high-contrast, clean, and readable at a glance. Use {{style_lock|a modern editorial product aesthetic}}. Do not invent extra UI labels or filler marketing copy.
```

### OG Cover Prompt

```text
Create an OG cover image for {{product_name|this product}}. Keep the exact headline "{{headline_lock|Launch smarter image workflows}}". Use minimal supporting text. Composition should be optimized for a wide social card, with clear breathing room around the text and one memorable visual metaphor based on {{visual_metaphor|the product's core workflow}}. Strong hierarchy, strong contrast, no clutter.
```

### Copy Repair Prompt

```text
Keep the same composition and general art direction. Repair only the copy rendering and text hierarchy. Preserve the exact locked words, increase readability, reduce extra text, and do not introduce new labels or slogans.
```

## Success Checks

- The image communicates one clear promise without reading the README
- All locked copy is rendered accurately enough to be usable
- The visual metaphor matches the actual product story
- The asset fits its target format without awkward cropping
- A user can explain what the product is from the image alone
