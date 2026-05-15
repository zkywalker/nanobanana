---
id: repo-explainer-diagram
type: workflow
title: 代码库讲解图
title_en: Repository Explainer Diagram
description: 读取 README、目录结构或代码摘要后，生成一张准确的项目结构/流程讲解图。
author: bananahub
license: CC-BY-4.0
version: 1.1.0
profile: diagram
tags: [代码库, 项目结构, 架构图, README, repo, codebase, architecture, explainer]
models:
  - name: gpt-image-2
    tested: false
    quality: best
  - name: gemini-3-pro-image-preview
    tested: false
    quality: good
  - name: gemini-3.1-flash-image-preview
    tested: false
    quality: good
providers:
  - id: openai
    family: gpt-image
    models:
      - id: gpt-image-2
        quality: best
        prompt_variant: gpt-image
      - id: gpt-image-1
        quality: ok
        prompt_variant: gpt-image
  - id: google-ai-studio
    family: gemini-image
    models:
      - id: gemini-3-pro-image-preview
        aliases: [nano-banana-pro]
        quality: good
        prompt_variant: gemini
      - id: gemini-3.1-flash-image-preview
        aliases: [nano-banana-2]
        quality: good
        prompt_variant: gemini
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
category: developer
samples: []
created: 2026-03-31
updated: 2026-05-15
---

## Goal

Turn real repository context into one clear visual: project map, architecture diagram, request flow, setup flow, or contributor onboarding card. Accuracy beats decoration.

## When To Use

- A README needs a first-glance project overview
- A new contributor needs to understand modules and data flow quickly
- A technical article or launch post needs one repo-aware diagram
- The user can provide local files, directory tree, README excerpts, or a source summary

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `source_material` | required | README excerpt, directory summary, code notes, or files the agent can inspect |
| `diagram_goal` | recommended | Architecture, request flow, setup flow, module map, or data flow |
| `audience` | optional | Contributors, maintainers, users, PMs, customers |
| `locked_blocks` | optional | Exact module/step labels that must appear |
| `style_lock` | optional | Product-doc, whiteboard, technical slide, or brand style |

## Steps

1. Read the available repo context first. Compress it into 3–7 verified blocks and relationships.
2. Pick one diagram goal. Do not mix architecture, setup, roadmap, and marketing copy in the same image.
3. Lock exact labels before generation. Prefer short module names over full implementation details.
4. Choose one layout: left-to-right pipeline, layered architecture, hub-and-spoke, grouped repo map, or top-to-bottom setup flow.
5. Generate with the provider-specific block. Prefer `gpt-image-2` for first-pass output when available because text fidelity and strict label control matter most for repo diagrams.
6. If the model invents modules, regenerate from a smaller source summary with a stricter label list.

## Prompt Blocks

### Planning Prompt

```text
Plan one concise repository explainer diagram for {{project_name|this project}}. Use only this verified source summary: {{source_summary|three to seven bullets from README, directory tree, or code notes}}. Return one diagram goal, one title, 3 to 7 exact block labels, and the verified relationships between them. Do not invent modules.
```

### Generation Prompt: gemini

```text
Create a clean repository explainer diagram for {{project_name|this project}}. Title: "{{title|Project Architecture Overview}}". Use {{layout|a left-to-right architecture layout}}. Include only these exact labeled blocks: {{locked_blocks|"Client", "API", "Worker", "Storage"}}. Show only these verified relationships: {{relationships|Client sends requests to API; API triggers Worker; Worker reads and writes Storage}}. Use {{style_lock|a modern product-doc diagram style with restrained colors, simple connectors, and generous spacing}}. Keep labels short, high-contrast, and easy to read.
```

### Generation Prompt: gpt-image

```text
Design one repository explainer diagram for {{project_name|this project}}. Title text: "{{title|Project Architecture Overview}}". Layout: {{layout|left-to-right architecture diagram}}. The only block labels allowed are: {{locked_blocks|"Client", "API", "Worker", "Storage"}}. Draw only these relationships: {{relationships|Client -> API; API -> Worker; Worker -> Storage}}. Style: {{style_lock|modern product-doc diagram, restrained colors, simple connectors, generous spacing}}. Do not add extra modules, paragraphs, fake file names, decorative code, watermarks, or tiny text.
```

### Repair Prompt

```text
Keep the same title, blocks, and relationships. Repair label accuracy, connector direction, spacing, and readability only. Remove any invented module or extra label.
```

## Provider Prompt Rules

### Provider Variant: gemini

Use the planning, generation, and repair blocks above as written for Gemini/Nano Banana. Keep the source summary, exact labels, and verified relationships explicit.

### Provider Variant: gpt-image

Use the same workflow steps, but keep visible text especially strict: exact title, exact block labels only, exact relationships only, no extra labels, no paragraphs, no fake file names, no decorative code, and no invented modules.

## Success Checks

- Every block maps to real source material
- The diagram has one obvious reading order
- Labels are short, readable, and not invented
- The image explains the repo faster than the README intro
- Omissions are acceptable; structural hallucinations are not
