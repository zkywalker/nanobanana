---
id: repo-explainer-diagram
type: workflow
title: 代码库讲解图工作流
title_en: Repository Explainer Diagram Workflow
description: 先读取 README、目录结构或代码摘要，再把代码库讲成一张结构清晰的信息图或架构讲解图。
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: diagram
tags: [代码库, 项目结构, 架构图, README, repo, codebase, architecture, explainer]
models:
  - name: gemini-3-pro-image-preview
    tested: true
    quality: best
  - name: gemini-3.1-flash-image-preview
    tested: false
    quality: good
aspect: "4:3"
difficulty: intermediate
category: docs
samples:
  - file: samples/sample-3-pro-01.png
    model: gemini-3-pro-image-preview
    prompt: "Create a clean explainer diagram for BananaHub. Title: 'BananaHub Architecture'. Use a left-to-right architecture layout. Include these exact labeled blocks: 'BananaHub Skill', 'BananaHub CLI', 'Hub API', 'Catalog Site', 'GitHub Templates'. Show only these verified relationships: the skill loads built-in and installed templates, the CLI installs templates from GitHub, the Hub API reports discovered installs, and the catalog site indexes curated and discovered templates. Keep labels short, high-contrast, and easy to read. Use a modern flat product-doc aesthetic with restrained blue, teal, and warm gray accents. Prioritize clarity over decoration."
    aspect: "4:3"
  - file: samples/sample-3-pro-02.png
    model: gemini-3-pro-image-preview
    prompt: "Create a clean repository explainer diagram for BananaHub. Title: 'BananaHub Template Flow'. Use a top-to-bottom workflow layout. Include these exact labeled blocks: 'User Request', 'Prompt Optimization', 'Profile Match', 'Template Suggestion', 'Generate or Edit'. Show only these verified relationships: the user request goes into prompt optimization, optimization leads to profile matching, profile matching can trigger template suggestion, and the final step is generate or edit. Keep labels short, high-contrast, and easy to read. Use a crisp flat explainer-card aesthetic with soft grid background, restrained teal and banana-gold accents, and simple directional connectors."
    aspect: "4:3"
created: 2026-03-31
updated: 2026-03-31
---

## Goal

Guide the agent through turning repository context into one clear explainer visual: a project map, architecture diagram, workflow chart, or onboarding card that reflects the actual repo structure instead of inventing generic boxes.

## When To Use

- A repo needs a quick visual introduction for onboarding
- README text is correct but too long for a first-pass explanation
- A project owner wants one image for docs, slides, or social sharing
- The user has local files, directory trees, or notes that should shape the diagram
- Accuracy of labels and module relationships matters more than flashy illustration

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `source_material` | recommended | README sections, local file paths, copied notes, or a directory summary that the agent can read first |
| `diagram_goal` | recommended | What the image should explain: architecture, request flow, setup steps, module map, data flow |
| `audience` | optional | New contributors, PMs, customers, internal team, open-source visitors |
| `copy_lock` | optional | Exact labels, titles, or bilingual text that must appear verbatim |
| `style_lock` | optional | Flat vector, notebook sketch, product docs aesthetic, whiteboard note, and so on |
| `layout_preference` | optional | Flowchart, layered architecture, left-to-right pipeline, hub-and-spoke, grid |
| `stop_condition` | optional | One clear explainer card, one architecture diagram, or one reusable onboarding visual |

## Steps

1. Read the available source material before prompting Gemini. If the repo context is broad, compress it into 3 to 7 blocks and name each block in plain language.
2. Decide the visual task first: architecture diagram, setup flow, repo map, or concept card. Do not mix multiple diagram goals in the same image unless the user explicitly asks for it.
3. Lock all exact labels before generation. If a title, section name, or step label matters, keep it verbatim and wrap it in quotes in the final prompt.
4. Choose one layout that matches the reading order. Prefer left-to-right for pipelines, top-to-bottom for setup flows, and grouped regions for repo maps.
5. Generate the first version with short labels, clear connectors, and restrained styling. Do not overload the first image with every implementation detail.
6. Review the output in this order: label accuracy, structural accuracy, reading order, then visual polish. If the diagram is pretty but structurally wrong, regenerate from the source summary.
7. If text rendering drifts, shorten labels instead of adding more microcopy. If one module is ambiguous, clarify the label outside the image and rerun.
8. Stop once the image communicates the repo's shape at a glance. This workflow is for explanation, not exhaustive documentation.

## Prompt Blocks

### Diagram Planning Prompt

```text
Plan one concise repository explainer diagram for {{project_name|this project}}. The diagram should explain {{diagram_goal|the main architecture and data flow}} for {{audience|new contributors}}. Use only the following verified source summary as truth: {{source_summary|three to six short blocks describing the repo}}. Propose one clean layout, one title, and short exact labels for each block. Avoid inventing modules that are not in the source summary.
```

### Diagram Generation Prompt

```text
Create a clean explainer diagram for {{project_name|this project}}. Title: "{{title|Project Architecture Overview}}". Use a {{layout_preference|left-to-right architecture layout}}. Include these exact labeled blocks: {{locked_blocks| "Client", "API", "Worker", "Storage" }}. Show only the verified relationships from the source summary: {{source_summary|client sends requests to API, API triggers worker, worker reads and writes storage}}. Keep labels short, high-contrast, and easy to read. Use {{style_lock|a modern flat product-doc aesthetic with restrained colors and simple connectors}}. Prioritize clarity over decoration.
```

### Layout Repair Prompt

```text
Keep the same diagram topic and the same exact labels. Repair only the structure and readability. Strengthen the reading order, prevent label overlap, increase contrast, and make the connectors unambiguous. Do not add new modules or extra copy.
```

## Success Checks

- Every major block in the image maps back to real source material
- The diagram has one obvious reading order without verbal explanation
- Labels are short enough to render cleanly and stay accurate
- The visual can be understood by the target audience in under ten seconds
- A reviewer can point to one or two omissions, not a full structural rewrite
