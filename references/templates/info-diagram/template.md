---
id: info-diagram
title: 信息图/流程图
title_en: Infographic & Flowchart
author: nanobanana
version: 1.0.0
profile: diagram
tags: [信息图, 流程图, 图表, 知识卡片, 教程]
models:
  - name: gemini-3.1-flash-image-preview
    tested: true
    quality: good
  - name: gemini-3-pro-image-preview
    tested: false
    quality: expected-best
aspect: "4:3"
difficulty: intermediate
samples:
  - file: samples/sample-3.1-flash-01.png
    model: gemini-3.1-flash-image-preview
    prompt: "Create a clean infographic about how coffee is made from bean to cup, in 5 steps: Harvest, Roast, Grind, Brew, Serve. Vertical flowchart layout with the 5 steps arranged top-to-bottom, each step inside a rounded box, connected by directional arrows. Modern flat vector design with rounded icons beside each step, using a warm pastel color palette of 3-4 colors. Each step has a bold short label in clear sans-serif font. Light gray background with subtle grid pattern. Professional information design with clear visual hierarchy, easy to read at a glance."
    aspect: "4:3"
created: 2026-03-24
updated: 2026-03-24
---

## 描述

生成清晰的信息图、流程图或知识卡片。结构化布局、图标化表达、层次分明的信息展示，适合技术文档、教程说明、社交媒体知识分享。

## Prompt Template

```
Create a clean infographic about {{topic|how coffee is made from bean to cup, in 5 steps: "Harvest", "Roast", "Grind", "Brew", "Serve"}}. {{layout|Vertical flowchart layout with the 5 steps arranged top-to-bottom, each step inside a rounded box, connected by directional arrows}}. {{style|Modern flat vector design with rounded icons beside each step, using a warm pastel color palette of 3-4 colors}}. {{labels|Each step has a bold short label (3-5 words max) in clear sans-serif font}}. {{background|Light gray background with subtle grid pattern}}. Professional information design with clear visual hierarchy, easy to read at a glance.
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `topic` | how coffee is made from bean to cup, in 5 steps: "Harvest", "Roast", "Grind", "Brew", "Serve" | 信息图主题，列出具体步骤/节点名称效果更好 |
| `layout` | Vertical flowchart layout with the 5 steps arranged top-to-bottom, each step inside a rounded box, connected by directional arrows | 布局类型：flowchart / comparison / timeline / hierarchy / isometric / grid |
| `style` | Modern flat vector design with rounded icons beside each step, using a warm pastel color palette of 3-4 colors | 视觉风格，flat design 和 vector 出图最干净 |
| `labels` | Each step has a bold short label (3-5 words max) in clear sans-serif font | 标签文字要求，短标签比长文本渲染更准确 |
| `background` | Light gray background with subtle grid pattern | 背景设置 |

## Usage Examples

**Basic**:
```
/nanobanana use info-diagram
```

**Custom topic**:
```
/nanobanana use info-diagram Git 工作流程：从 commit 到 merge 的 4 个步骤
```

**Comparison layout**:
```
/nanobanana use info-diagram React vs Vue 对比，左右两栏对比布局
```

**Timeline**:
```
/nanobanana use info-diagram AI 发展时间线，从 1950 到 2026，水平时间轴
```

## Tips

- Pro model strongly recommended — better text rendering and layout precision
- Keep content to 5-8 key points maximum; Gemini degrades with complex diagrams (labels overlap, arrows cross)
- List your exact step/node names in quotes inside the topic variable — explicit labels render far more accurately than letting the model invent them
- Specify the exact number of steps/sections for better layout control
- Use "flat vector design" or "minimal icons" for cleaner results than realistic illustrations
- For Chinese labels, wrap text in quotes: 写着"第一步"
- 4:3 ratio works for most infographics; use 9:16 for vertical social media cards
- AI-generated text may contain errors — always verify factual content in the output
- For complex diagrams (>8 nodes), consider breaking into multiple simpler diagrams or using dedicated tools (Mermaid, draw.io)
- Generate the layout/structure first, then add data — this produces cleaner results than trying to do both at once
