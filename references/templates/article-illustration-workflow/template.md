---
id: article-illustration-workflow
type: workflow
title: 文章配图工作流
title_en: Article Illustration Workflow
description: 先读取文章或段落，再规划配图大纲，逐张生成适合博客、教程和文档的说明图或 editorial visual。
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: diagram
tags: [文章配图, 文章插图, 博客配图, 教程配图, blog, article, editorial, tutorial, docs, explainer]
models:
  - name: gemini-3-pro-image-preview
    tested: false
    quality: best
  - name: gemini-3.1-flash-image-preview
    tested: false
    quality: good
aspect: "16:9"
difficulty: intermediate
category: docs
samples:
  - file: samples/sample-3-pro-01.png
    model: gemini-3-pro-image-preview
    prompt: "Create a clean article-support workflow diagram. Use only these verified facts as truth: the workflow starts by extracting verified claims from the article; it plans image slots before any generation; it generates one image at a time and reviews fidelity. Show exactly three grouped stages in a left-to-right reading order. The only text allowed anywhere in the image is: \"Extract claims\", \"Plan slots\", and \"Generate + review\". Do not add a title, caption, paragraph, badge, or any extra words. Use a restrained product-doc editorial aesthetic with warm paper-white background, ink-black linework, and muted banana-gold and teal accents. Keep the image text-light, high-contrast, and easy to understand in under ten seconds."
    aspect: "16:9"
  - file: samples/sample-3-pro-02.png
    model: gemini-3-pro-image-preview
    prompt: "Create a compact article-support planning card. Use only these verified facts as truth: not every paragraph needs a picture; some sections want a flowchart; some need a framework card; some are better left text-only. Use a clean three-column comparison card with obvious visual separation. The only text allowed anywhere in the image is: \"Flowchart\", \"Framework card\", and \"Text only\". Do not add a title, caption, paragraph, badge, or any extra words. Use a restrained product-doc editorial aesthetic with warm paper-white background, ink-black linework, and muted banana-gold and teal accents. Keep the image text-light, high-contrast, and understandable in under ten seconds."
    aspect: "4:3"
  - file: samples/sample-3-pro-03.png
    model: gemini-3-pro-image-preview
    prompt: "Create a scene-led editorial cover image for an article about planning illustrations. Use only these verified facts as truth: good article visuals should clarify the writing instead of distracting from it; the workflow reads the article first; image slots are decided later. Show a calm editorial desk scene with one printed article page as the focal object, a pencil, and three small unlabeled thumbnail frames placed nearby to suggest planning. No text anywhere in the image. Use a restrained warm editorial aesthetic with paper-white surfaces, ink-black details, and muted banana-gold and teal accents. Keep the composition clean, thoughtful, and suitable as a section cover rather than a technical diagram."
    aspect: "3:4"
created: 2026-04-03
updated: 2026-04-03
---

## Goal

Guide the agent through turning an article, tutorial, or one important paragraph into a compact illustration pack: read the source first, decide which sections deserve images, write a small outline, then generate visuals that clarify the article instead of decorating it.

## When To Use

- A blog post, docs page, or tutorial needs one image per major section
- A long article is easier to understand with 1 to 4 explanatory visuals
- A single paragraph needs one supporting concept card, comparison, framework, or timeline
- The user wants Markdown image refs inserted back into the article after generation
- Factual fidelity and paragraph-to-image alignment matter more than flashy standalone art

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `source_material` | recommended | Article path, pasted Markdown, copied section text, or one paragraph that should drive the visuals |
| `illustration_scope` | recommended | `single-paragraph`, `single-section`, `per-section`, or `one-hero-visual` |
| `density_lock` | optional | A cap such as `1 image`, `2 images`, or `one image per major section` |
| `visual_family` | optional | Infographic, framework, comparison, timeline, flowchart, or scene-led editorial visual |
| `style_lock` | optional | Product-doc, Notion-like, blueprint, warm editorial, notebook sketch, and so on |
| `copy_lock` | optional | Exact titles, labels, or short phrases that must appear verbatim in the image |
| `output_dir` | optional | Where to save `outline.md` and generated images; default to an `imgs/` folder near the article when possible |
| `insert_mode` | optional | Whether to insert Markdown image refs back into the article after approval |
| `approved_baseline` | optional | Accepted image file for later edit rounds when the user wants to refine an existing illustration |

## Steps

1. Detect the entry mode first: article file, pasted article, single paragraph, or follow-up edit from an accepted image. Read the source before writing any generation prompt.
2. Compress the source into 2 to 6 verified claims or sections. Decide whether each candidate image should explain a concept, summarize a process, compare options, show a framework, or act as one scene-led section cover. Do not literalize metaphors when the article is abstract.
3. Ask only for missing blockers: illustration scope, density cap, visual family, style lock, output directory, and whether the article should be updated with Markdown image refs.
4. Write a compact outline file such as `imgs/outline.md`. For each image slot, record the section anchor, visual goal, locked facts, visual type, aspect ratio, and filename using `NN-type-slug.png`.
5. Generate one image at a time from the outline. Prefer `16:9` or `4:3` for explainers, `1:1` for compact framework cards, and `3:4` only when a slot is clearly scene-led.
6. Review each image in this order: article fidelity, paragraph-to-image match, text accuracy, reading order, then style consistency. If a result looks attractive but drifts from the article, regenerate from the locked facts instead of adding more decorative language.
7. If `insert_mode` is enabled, insert `![alt text](imgs/NN-type-slug.png)` after the matching heading or paragraph. Keep alt text descriptive and tied to the article claim, not promotional.
8. Once an image is accepted, treat it as the approved baseline. Later changes should be edit rounds with locked invariants and one allowed delta, not full rewrites from scratch.

## Prompt Blocks

### Outline Planning Prompt

```text
Plan a compact illustration pack for {{article_title|this article}}. The scope is {{illustration_scope|one image per major section}} for {{audience|readers who need a fast visual explanation}}. Use only the following verified article summary as truth: {{source_summary|three to six short claims or sections}}. For each proposed image, specify the section anchor, the visual goal, the recommended visual_type, the aspect ratio, and a short filename slug. Prefer concept-level explanation over literal depiction of metaphors or decorative filler.
```

### Article Illustration Prompt

```text
Create an article-support visual for {{article_title|this article}}. The image should support the section "{{section_anchor|Introduction}}". Use only these verified facts as truth: {{locked_facts|three short factual bullets from the article}}. The visual goal is {{visual_goal|explain one core concept at a glance}}. Use a {{visual_type|clean infographic}} composition with {{layout_preference|clear grouping and obvious reading order}}. Keep any exact labels or short copy verbatim: {{copy_lock|"Input", "Process", "Output"}}. If no exact labels are required, keep the image text-light. Use {{style_lock|a restrained product-doc or editorial explainer aesthetic}}. Avoid literalizing metaphors, extra data, or decorative scene elements that are not supported by the article.
```

### Article Repair Prompt

```text
Keep the same article claim and the same locked facts. Repair only clarity, reading order, and article fidelity. Shorten labels, remove decorative elements that are not supported by the text, and make the main concept understandable in under ten seconds. Do not introduce new claims or extra copy.
```

## Success Checks

- Every accepted image maps back to one verified section, paragraph, or claim
- The article becomes easier to skim with the visuals than without them
- Any locked labels or short copy stay accurate enough to use, or are omitted
- The image pack shares one coherent visual family without making every slot look identical
- Follow-up edits can continue from accepted files with locked invariants and stable filenames
