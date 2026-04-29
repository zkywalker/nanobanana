---
id: background-replace-edit
type: prompt
title: 背景替换编辑
title_en: Background Replacement Edit
description: 保留主体不变，只替换图片背景，适合商品、人像、证件照、海报和社媒素材二次加工。
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: photo
tags: [背景替换, 图片编辑, 商品编辑, 人像编辑, background, edit, retouch]
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
  generation: false
  edit: true
  mask_edit: false
prompt_variants:
  default: base
  gemini: prompt-gemini
  gpt-image: prompt-gpt-image
aspect: "source"
difficulty: beginner
category: editing
samples: []
created: 2026-04-29
updated: 2026-04-29
---

## 描述

用于已有图片的背景替换。核心原则是主体、姿态、产品结构、文字和关键边缘尽量不动，只改变环境、光线和氛围。

## Prompt Template

```text
Using the provided source image, replace only the background with {{new_background|a clean modern studio setting with warm off-white walls and soft floor shadows}}. Preserve {{subject_lock|the original subject, pose, proportions, product shape, clothing, facial features, labels, and visible text}}. Match {{lighting_match|natural lighting direction, realistic contact shadows, and believable color reflection}}. Keep edges clean and avoid changing the subject, adding new objects, distorting logos, or altering important details.
```

## Prompt Template: gemini

```text
Edit the provided source image. Replace only the background with {{new_background|a clean modern studio setting with warm off-white walls and soft floor shadows}}. Preserve {{subject_lock|the original subject, pose, proportions, product shape, clothing, facial features, labels, and visible text}} exactly as much as possible. Match {{lighting_match|natural lighting direction, realistic contact shadows, and believable color reflection}} so the subject feels native to the new scene. Keep edges clean. Do not alter the subject or invent extra objects.
```

## Prompt Template: gpt-image

```text
Edit the source image by changing the background only. New background: {{new_background|a clean modern studio setting with warm off-white walls and soft floor shadows}}. Keep unchanged: {{subject_lock|the original subject, pose, proportions, product shape, clothing, facial features, labels, and visible text}}. Match {{lighting_match|lighting direction, contact shadows, scale, and color reflection}}. Do not change the subject, logo, text, face, product geometry, clothing, hands, edges, or foreground details. Do not add extra props unless requested.
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `new_background` | a clean modern studio setting with warm off-white walls and soft floor shadows | 新背景 |
| `subject_lock` | the original subject, pose, proportions, product shape, clothing, facial features, labels, and visible text | 必须保持不变的主体信息 |
| `lighting_match` | natural lighting direction, realistic contact shadows, and believable color reflection | 光影匹配要求 |

## Tips

- 这个模板需要 `--input <image>`；没有源图时不要当作普通文生图使用。
- 背景替换最怕主体漂移，先写清楚“不要改什么”，再写新背景。
- 需要精确局部编辑时，优先选择支持 mask 的 provider/model；模板本身不假设 mask 是跨模型通用能力。
- 商品图保留 logo 和包装文字，人像保留脸型和服装，宠物保留姿态和毛色。
- 如果第一次边缘不干净，用 repair prompt 要求只修边缘、阴影和融合，不要重画主体。
