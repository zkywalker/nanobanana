---
id: info-diagram
type: prompt
title: 信息图一页卡
title_en: Practical Infographic One-Pager
description: 把步骤、对比、时间线或框架压缩成一张清晰可读的信息图。
author: bananahub
license: CC-BY-4.0
version: 1.1.0
profile: diagram
tags: [信息图, 一页图, 流程图, 知识卡片, infographic, diagram, one-pager]
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
difficulty: beginner
category: diagram
samples:
  - file: samples/sample-3.1-flash-01.png
    provider: google-ai-studio
    model: gemini-3.1-flash-image-preview
    prompt_variant: gemini
    prompt: "Create a tall infographic titled \"How Coffee Is Made: Bean to Cup\". Use exactly five stacked steps with these labels: \"Harvest\", \"Roast\", \"Grind\", \"Brew\", \"Serve\". Use warm coffee colors, simple icons, rounded cards, and clear arrows. Keep the layout readable and do not add extra steps."
    aspect: "4:3"
created: 2026-03-24
updated: 2026-05-16
---

## 描述

生成稳定、实用的信息图一页卡。适合流程说明、概念拆解、对比图、时间线和教程摘要。目标不是炫技，而是让读者 10 秒内看懂结构。

## Prompt Template

```text
Create a clean infographic one-pager about {{topic|how a pull request moves from code change to merge}}. Use {{layout|a left-to-right 5-step flow with rounded cards and simple arrows}}. Include only these exact labels: {{labels|"Change", "Review", "Test", "Fix", "Merge"}}. Use {{style|flat vector information design, simple icons, generous spacing, and a restrained blue/teal palette}} on {{background|a warm off-white background with a subtle grid}}. Keep hierarchy clear, labels short, connectors unambiguous, and avoid extra facts or decorative clutter.
```

## Prompt Template: gemini

```text
Create a clean infographic one-pager about {{topic|how a pull request moves from code change to merge}}. Use {{layout|a left-to-right 5-step flow with rounded cards and simple arrows}}. Include only these exact labels: {{labels|"Change", "Review", "Test", "Fix", "Merge"}}. Use {{style|flat vector information design, simple icons, generous spacing, and a restrained blue/teal palette}} on {{background|a warm off-white background with a subtle grid}}. Keep the layout balanced, arrows non-overlapping, icons minimal, and text easy to read. Do not invent extra steps.
```

## Prompt Template: gpt-image

```text
Design one infographic card about {{topic|how a pull request moves from code change to merge}}. Layout: {{layout|exactly 5 rounded cards in a left-to-right flow, connected by simple arrows}}. The only text allowed in the image is: {{labels|"Change", "Review", "Test", "Fix", "Merge"}}. Style: {{style|flat vector information design, simple icons, generous spacing, restrained blue/teal palette}}. Background: {{background|warm off-white with a subtle grid}}. Avoid paragraphs, captions, extra labels, invented facts, crossed arrows, tiny text, clutter, and decorative filler.
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `topic` | how a pull request moves from code change to merge | 信息图主题，最好明确步骤/对比/时间线类型 |
| `layout` | a left-to-right 5-step flow with rounded cards and simple arrows | 布局方式和节点数量 |
| `labels` | "Change", "Review", "Test", "Fix", "Merge" | 需要出现在图中的短标签 |
| `style` | flat vector information design, simple icons, generous spacing, and a restrained blue/teal palette | 视觉风格 |
| `background` | a warm off-white background with a subtle grid | 背景要求 |

## Tips

- 先把 `labels` 锁死，再生成；不要让模型自由编写长段文字。
- 一张图控制在 3–7 个节点，复杂内容拆成多张。
- 中文标签可以直接写进 `labels`，但要短，例如 `"需求", "开发", "评审", "上线"`。
- GPT Image 分支更适合严格限制“只出现这些文字”；Gemini 分支适合更自然的图标和版式探索。
- 信息图不是事实来源，涉及数字、流程和结论时必须由用户或 agent 先确认。
