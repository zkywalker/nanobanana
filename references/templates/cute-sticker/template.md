---
id: cute-sticker
title: Q版贴纸表情包
title_en: Cute Chibi Sticker Pack
author: nanobanana
version: 1.0.0
profile: sticker
tags: [贴纸, 表情包, Q版, 可爱, chibi]
models:
  - name: gemini-3.1-flash-image-preview
    tested: true
    quality: good
  - name: gemini-3-pro-image-preview
    tested: false
    quality: expected-best
  - name: gemini-2.0-flash-preview-image-generation
    tested: false
    quality: unknown
aspect: "1:1"
difficulty: beginner
samples:
  - file: samples/sample-3.1-flash-01.png
    model: gemini-3.1-flash-image-preview
    prompt: "A cute chibi sticker of a round fluffy cat, happy and excited with oversized sparkly eyes and a wide open smile, waving both paws enthusiastically. Kawaii anime style with bold black outline, flat cel-shaded colors, and clean white background. Super deformed proportions with an oversized head (head-to-body ratio 1:1), die-cut sticker-ready composition, simple rounded shapes, vibrant pastel-accented colors."
    aspect: "1:1"
created: 2026-03-24
updated: 2026-03-24
---

## 描述

生成 Q 版可爱贴纸/表情包。大头小身、表情夸张、白色背景带描边，适合微信/Telegram 表情包或社交媒体贴纸。

## Prompt Template

```
A cute chibi sticker of {{subject|a round fluffy cat}}, {{expression|happy and excited with oversized sparkly eyes and a wide open smile}}, {{action|waving both paws enthusiastically}}. {{style|Kawaii anime style with bold black outline, flat cel-shaded colors, and clean white background}}. Super deformed proportions with an oversized head (head-to-body ratio 1:1), die-cut sticker-ready composition, simple rounded shapes, vibrant pastel-accented colors.
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `subject` | a round fluffy cat | 贴纸主角，可以是动物、人物、食物、物品等。保持简单，一个角色即可 |
| `expression` | happy and excited with oversized sparkly eyes and a wide open smile | 表情/情绪，表情包的灵魂。越夸张越好 |
| `action` | waving both paws enthusiastically | 动作/姿态，简单明确的单一动作 |
| `style` | Kawaii anime style with bold black outline, flat cel-shaded colors, and clean white background | 画风、描边、上色风格 |

## Usage Examples

**Basic**:
```
/nanobanana use cute-sticker
```

**Custom character**:
```
/nanobanana use cute-sticker 一只柴犬，露出嫌弃的表情
```

**Custom emotion**:
```
/nanobanana use cute-sticker 小恐龙，哭泣委屈的样子，抱着一个枕头
```

## Tips

- Emotion IS the content for stickers — exaggerated expressions work best
- Keep it to 3 elements max: the character, one prop/accessory, and optionally one text element
- Specify head-to-body ratio explicitly (1:1 for maximum chibi, 1:1.5 for slightly taller)
- "die-cut sticker-ready composition" and "white background" help create clean sticker borders
- "flat cel-shaded colors" and "bold outlines" produce cleaner results than detailed shading
- For a sticker set, keep the same subject description and style, only change expression and action
- Flash model works well for simple sticker styles; Pro for more detailed or textured ones
- Avoid complex backgrounds — stickers must be instantly readable at small sizes (128-512px)
- If including text, keep it to 1-4 words max in bold outlined text
