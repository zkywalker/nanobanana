---
id: article-one-page-summary
type: workflow
title: 文章一图流解读
title_en: Article One-Page Visual Summary
description: 先提炼文章主张和结构，再生成一张适合转发、汇报或文档首屏的一图流解读。
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: diagram
tags: [文章解读, 一图流, 长文总结, 知识卡片, article, summary, infographic, one-pager]
models:
  - name: gemini-3-pro-image-preview
    tested: false
    quality: best
  - name: gemini-3.1-flash-image-preview
    tested: false
    quality: good
  - name: gpt-image-2
    tested: false
    quality: best
providers:
  - id: google-ai-studio
    family: gemini-image
    models:
      - id: gemini-3-pro-image-preview
        aliases: [nano-banana-pro]
        quality: best
        prompt_variant: gemini
      - id: gemini-3.1-flash-image-preview
        aliases: [nano-banana-2]
        quality: good
        prompt_variant: gemini
  - id: openai
    family: gpt-image
    models:
      - id: gpt-image-2
        quality: best
        prompt_variant: gpt-image
      - id: gpt-image-1
        quality: ok
        prompt_variant: gpt-image
capabilities:
  generation: true
  edit: false
  mask_edit: false
prompt_variants:
  default: base
  gemini: prompt-gemini
  gpt-image: prompt-gpt-image
aspect: "4:3"
difficulty: intermediate
category: content
samples: []
created: 2026-04-29
updated: 2026-04-29
---

## Goal

Turn an article, memo, transcript, or long note into one accurate visual summary. The workflow protects facts first, then compresses the message into a readable one-page infographic.

## When To Use

- A user gives an article and wants one shareable explainer image
- A long document needs a first-screen summary for docs, slides, or social posts
- The source has claims, steps, trade-offs, or a framework that should not be distorted
- The image should explain the content, not create a generic editorial illustration

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `source_text` | required | Article text, outline, URL excerpt, transcript, or notes |
| `audience` | recommended | Readers: beginners, executives, developers, customers, students |
| `takeaway` | recommended | The one-sentence message the image must communicate |
| `locked_labels` | optional | Exact terms, numbers, or Chinese/English labels that must remain unchanged |
| `brand_style` | optional | Color, tone, layout, or publication style |

## Steps

1. Read the source before image prompting. Extract 1 core takeaway, 3–5 supporting points, and any exact labels or numbers that must not change.
2. Ask for missing blockers only when the source lacks a clear takeaway or the target audience is unknown.
3. Choose one structure: pyramid, 3-part framework, timeline, comparison, or flow. Do not combine multiple structures in the first image.
4. Lock the text set. Keep the title and labels short; move nuance to the chat response, not into the image.
5. Generate with the provider-specific prompt block. Prefer `gpt-image-2` when exact text limits matter most; prefer Gemini/Nano Banana when layout exploration or reference images matter more.
6. Review in this order: factual accuracy, text fidelity, reading order, then visual polish.
7. If the output invents facts or adds extra labels, regenerate with a smaller locked text set instead of adding more prose.

## Prompt Blocks

### Source Compression Prompt

```text
Extract one visual summary plan from {{source_text|the provided article}} for {{audience|busy readers}}. Return: one short title, one core takeaway, 3 to 5 supporting points, exact labels/numbers that must stay unchanged, and the best layout type. Do not add facts that are not in the source.
```

### Generation Prompt: gemini

```text
Create one clean article-summary infographic for {{audience|busy readers}}. Title: "{{title|What Changes After AI Agents Join the Workflow}}". Core takeaway: {{takeaway|agents shift work from manual execution to review and orchestration}}. Use {{layout|a three-part framework layout with one central takeaway and three supporting cards}}. Include only these exact short labels: {{locked_labels|"Delegate", "Review", "Orchestrate"}}. Use {{brand_style|modern editorial information design, warm off-white background, dark ink text, banana-gold and teal accents, simple line icons}}. Keep the image text-light, balanced, and readable in under ten seconds. Do not invent statistics or claims.
```

### Generation Prompt: gpt-image

```text
Design one article-summary infographic for {{audience|busy readers}}. Title text: "{{title|What Changes After AI Agents Join the Workflow}}". Main message: {{takeaway|agents shift work from manual execution to review and orchestration}}. Layout: {{layout|one central takeaway plus exactly three supporting cards}}. The only supporting labels allowed are: {{locked_labels|"Delegate", "Review", "Orchestrate"}}. Visual style: {{brand_style|modern editorial information design, warm off-white background, dark ink text, banana-gold and teal accents, simple line icons}}. Do not add paragraphs, extra labels, fake numbers, invented claims, watermarks, or decorative filler. Keep all text large and legible.
```

### Repair Prompt

```text
Keep the same article topic, title, takeaway, and exact labels. Repair only factual fidelity, text legibility, spacing, and reading order. Remove any invented labels, extra claims, fake numbers, or decorative clutter.
```

## Success Checks

- The title, labels, and numbers match the source or user-approved summary
- A reader can understand the main idea in under ten seconds
- The image contains one structure, not a crowded article screenshot
- No unsupported statistics, quotes, or claims appear in the output
- The result works as a cover image, slide opener, or shareable one-pager
