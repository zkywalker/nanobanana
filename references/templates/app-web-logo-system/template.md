---
id: app-web-logo-system
type: workflow
title: App/Web Logo 生成工作流
title_en: App and Web Logo Workflow
description: 先锁定品牌语义、平台约束和小尺寸识别，再生成 app 图标、favicon、字标和单色版。
author: bananahub
license: CC-BY-4.0
version: 1.0.0
profile: text-heavy
tags: [logo, app图标, web logo, favicon, 品牌标识, icon, wordmark, maskable]
models:
  - name: gemini-3-pro-image-preview
    tested: true
    quality: best
  - name: gemini-3.1-flash-image-preview
    tested: false
    quality: good
aspect: "1:1"
difficulty: intermediate
category: branding
samples:
  - file: samples/sample-3-pro-01.png
    model: gemini-3-pro-image-preview
    prompt: "Create an icon-first logo system sample for BananaHub. Use one bold black peeled-banana symbol as the approved core mark, keep it centered and high-contrast on a warm off-white presentation board, and show two outputs from the same baseline: one square app-icon-safe symbol and one clean website lockup with the exact wordmark 'BananaHub'. Keep the palette monochrome, flat, and minimal. No gradients, no mascots, no extra copy beyond the locked brand name and short usage labels."
    aspect: "1:1"
created: 2026-04-01
updated: 2026-04-02
---

## Goal

Guide the agent through building a usable app and web logo system: first lock the brand idea and the most restrictive platform constraints, then generate an icon-first mark, then derive web lockups and platform-safe variants without letting the concept drift.

## When To Use

- A new product needs an app icon and website logo from the same core mark
- The team wants icon-only, wordmark, favicon, or monochrome variants from one visual idea
- Small-size legibility matters more than decorative detail
- The user is still exploring concepts, but wants platform-aware outputs instead of generic logo art
- Gemini should help with concept generation, not replace final vector cleanup

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `brand_name` | recommended | Exact product or company name |
| `brand_brief` | recommended | One-sentence description of what the product does and how it should feel |
| `surface_priority` | recommended | The most restrictive target first: iOS app icon, Android launcher icon, Google Play icon, PWA icon, favicon, website header |
| `logo_mode` | recommended | icon-only, initials, wordmark, or combination mark |
| `approved_baseline` | optional | The accepted master logo file that all later variants must follow exactly |
| `symbol_direction` | optional | Shape or metaphor direction, such as spark, banana slice, shield, or monogram |
| `palette_lock` | optional | Brand colors or a simple color rule |
| `must_keep` | optional | Existing letters, symbols, negative-space ideas, or geometry that must stay |
| `must_avoid` | recommended | Gradients, mascots, 3D chrome, extra text, tiny details, copied motifs, and so on |
| `delivery_goal` | optional | Which variants must ship now: icon-only, wordmark, monochrome, maskable icon, store icon, favicon |

## Steps

1. Lock the brief before prompting. Compress the brand into one core idea, one desired tone, and one or two non-negotiable constraints. If the name or initials are not final, do not force text into the first round.
2. Start from the most constrained surface. Default to a square icon-first mark for app icon and favicon use, because a website lockup is easier to derive later than the reverse.
3. Generate one simple centered symbol first. Prefer a strong silhouette, restrained palette, and clean negative space. Avoid mockups, perspective scenes, UI screenshots, shiny materials, and tiny interior detail.
4. Review the icon at small sizes before expanding the system. If it stops reading at roughly 16 to 32 pixels, simplify shapes and internal cuts instead of adding polish.
5. After the icon is approved, mark that file as the `approved_baseline`. All later variants must keep the exact core silhouette, peel count, border logic, and proportion system unless the user explicitly reopens them.
6. Derive only one secondary variant at a time: wordmark lockup, monochrome version, maskable or adaptive-icon version, or store-listing version. Keep the core concept unchanged.
7. Use the model only for creative refinements that still need interpretation. For deterministic derivatives such as invert, add padding, resize, export, or place the approved icon beside exact final text, prefer local deterministic transforms.
8. Apply platform repair rules when needed. Apple-style icons want one clear focal idea; Android adaptive and maskable icons need generous safe padding inside the square; Google Play icons should not depend on rounded corners or baked drop shadows.
9. Stop when the same mark works in color, monochrome, and small-size use. If one target surface fails, repair that surface-specific variant instead of redesigning the whole brand.

## Prompt Blocks

### Icon Concept Prompt

```text
Create a square app icon concept for {{brand_name|this product}}. The brand is {{brand_brief|a calm, reliable AI workspace for developers}}. Use {{symbol_direction|one simple geometric symbol}} as the core idea. Keep the mark centered, flat, high-contrast, and easy to recognize at favicon size. Use {{palette_lock|a restrained two-color palette}}. No mockup, no UI, no photo texture, no tiny details, no extra text.
```

### Wordmark Lockup Prompt

```text
Create a clean website logo lockup for {{brand_name|this product}}. Keep the approved symbol unchanged. Add the exact text "{{wordmark_text|BRAND}}" only if it is final. Use {{type_direction|clean distinctive sans-serif letterforms with clear spacing}}. Keep the composition simple, brand-ready, and usable in a website header. No slogan, no filler copy, no decorative background.
```

### Maskable Icon Prompt

```text
Create a platform-safe app icon variant for {{brand_name|this product}}. Keep the important symbol fully inside a centered safe zone with generous padding. Use {{background_style|one solid brand-color background}} and keep the foreground clean and uncluttered. No corner radius, no drop shadow, no border, no extra text.
```

### Monochrome Repair Prompt

```text
Keep the same logo idea and simplify it for tiny sizes. Produce a monochrome version with clean edges, fewer internal cuts, stronger silhouette, and readable negative space at 16 to 32 pixels. Do not change the core concept, only reduce detail and improve legibility.
```

### Baseline-Lock Prompt

```text
Use the approved baseline logo as the only source of truth. Keep the exact silhouette, exact peel count, exact rounded fruit flesh shape, exact border thickness, and exact spacing unchanged. Change only {{allowed_delta|the background to solid black and the mark to white}}. Do not redraw, reinterpret, restyle, reshape, recompose, or add details.
```

## Success Checks

- The icon is still recognizable when shrunk to favicon or launcher-icon size
- The logo idea works without relying on long text or decorative effects
- The important symbol sits safely inside a centered square area for masked platforms
- The mark still reads in monochrome
- Wordmark versions keep exact locked text and do not add filler copy
- Each accepted iteration changes one major variable instead of rewriting the whole concept
