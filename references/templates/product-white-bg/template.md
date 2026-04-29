---
id: product-white-bg
type: prompt
title: 电商白底产品图
title_en: E-commerce Product Clean Shot
description: 为商品主图、目录图和详情页首屏生成干净、可信、可复用的白底棚拍图。
author: bananahub
license: CC-BY-4.0
version: 1.1.0
profile: product
tags: [产品图, 电商, 白底, 商品主图, catalog, ecommerce, product]
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
  edit: true
  mask_edit: false
prompt_variants:
  default: base
  gemini: prompt-gemini
  gpt-image: prompt-gpt-image
aspect: "1:1"
difficulty: beginner
category: ecommerce
samples: []
created: 2026-03-24
updated: 2026-04-29
---

## 描述

生成电商平台常用的白底产品图。重点是主体干净、材质可信、边缘完整、投影自然，适合主图、目录图、详情页首屏和内部选品物料。

## Prompt Template

```text
Create a clean studio catalog product image of {{product|a matte black wireless earbud charging case with subtle logo embossing}}. Show it in {{angle|a front three-quarter hero angle}} on {{background|a pure white background with a small natural contact shadow}}. Use {{lighting|soft three-point studio lighting with a diffused key light and gentle rim light}}. Emphasize {{material_detail|accurate material texture, crisp edges, and realistic scale}}. Keep the product isolated, centered, uncropped, and free of props, people, badges, watermarks, or extra text.
```

## Prompt Template: gemini

```text
Create a photorealistic studio catalog product image of {{product|a matte black wireless earbud charging case with subtle logo embossing}}. Use {{angle|a front three-quarter hero angle}} and place the product on {{background|a pure white background with a small natural contact shadow}}. Use {{lighting|soft three-point studio lighting with a diffused key light, subtle fill, and gentle rim light}}. Preserve {{material_detail|accurate material texture, crisp edges, realistic scale, and clean reflections}}. Keep the product isolated, centered, uncropped, and free of lifestyle props, people, badges, watermarks, or extra text.
```

## Prompt Template: gpt-image

```text
Create a commercial white-background product shot of {{product|a matte black wireless earbud charging case with subtle logo embossing}}. Composition: {{angle|front three-quarter hero angle}}, centered, product fills most of the frame, no cropped edges. Background: {{background|pure white with one small realistic contact shadow}}. Lighting: {{lighting|soft three-point studio lighting with a diffused key light and gentle rim light}}. Render {{material_detail|accurate material texture, crisp seams, clean edges, and realistic scale}}. Do not add props, people, marketing badges, paragraphs, fake logos, watermarks, duplicated parts, or extra objects.
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `product` | a matte black wireless earbud charging case with subtle logo embossing | 商品名称、颜色、材质和关键特征 |
| `angle` | a front three-quarter hero angle | 拍摄角度：正面、侧面、俯拍、45 度主图 |
| `background` | a pure white background with a small natural contact shadow | 背景和投影要求 |
| `lighting` | soft three-point studio lighting with a diffused key light and gentle rim light | 灯光方案 |
| `material_detail` | accurate material texture, crisp edges, and realistic scale | 材质、边缘、比例等质量重点 |

## Tips

- 商品图是低维护、高复用模板：先把主体、角度、材质写清楚，再谈风格。
- 有真实商品图时优先走 `edit --input` 或 `--ref`，不要让模型重新发明结构。
- 带文字或 logo 的商品要明确哪些文字必须保留，生成后人工复核。
- GPT Image 分支更强调“不要添加假元素”；Gemini 分支更强调材质、反光和自然投影。
- 白底主图保持 `1:1`；详情页横幅可手动改 `--aspect 4:3` 或 `16:9`。
