# Template Format Spec

Authoritative reference for `template.md` structure, repo layout, and type-specific requirements.

## Repo Structure

A template repo can contain one or multiple templates:

**Single-template repo**

```text
/
├── template.md
├── samples/                 # Optional during iteration, recommended for publishing
│   ├── sample-3-pro-01.png
│   └── sample-3.1-flash-01.png
├── README.md
└── LICENSE
```

**Multi-template repo**

```text
/
├── bananahub.json
├── info-diagram/
│   └── template.md
├── article-one-page-summary/
│   └── template.md
└── README.md
```

**`bananahub.json`** (multi-template repo manifest):

```json
{
  "type": "multi",
  "templates": ["info-diagram", "article-one-page-summary"]
}
```

## `template.md` Complete Field Reference

```yaml
---
# === Identity ===
id: article-one-page-summary            # Unique ID (lowercase, hyphens, 3-50 chars)
type: workflow                           # prompt | workflow
title: 文章一图流解读
title_en: Article One-Page Visual Summary
description: 把文章压缩成一张可读信息图    # Optional short description
author: github-username
license: CC-BY-4.0
version: 1.0.0

# === Generation Config ===
profile: diagram
aspect: "4:3"
models:
  - name: gemini-3-pro-image-preview
    quality: best
  - name: gemini-3.1-flash-image-preview
    quality: good
providers:
  - id: google-ai-studio
    family: gemini-image
    models:
      - id: gemini-3-pro-image-preview
        aliases: [nano-banana-pro]
        quality: best
        prompt_variant: gemini
  - id: openai
    family: gpt-image
    models:
      - id: gpt-image-2
        quality: untested
        prompt_variant: gpt-image
capabilities:
  generation: true
  edit: false
  mask_edit: false
prompt_variants:
  default: base
  gemini: prompt-gemini
  gpt-image: prompt-gpt-image

# === Discovery ===
tags: [文章解读, 一图流, article, summary, infographic]
difficulty: intermediate
category: content

# === Sample Images ===
samples: []                              # Starter templates can stay sample-free; published hub templates should include samples when practical

# === Metadata ===
created: 2026-04-29
updated: 2026-04-29
---
```

### Required vs Optional Fields

| Field | Required | Used By |
|-------|----------|---------|
| `id` | Yes (or derived from dirname) | CLI install, listing, matching |
| `type` | Recommended (`prompt` default if missing) | Type-aware activation |
| `title` | Yes | Listing, Hub display |
| `title_en` | Yes | Hub display, English search |
| `description` | Recommended | Hub cards, listing |
| `author` | Yes | Attribution |
| `license` | Recommended locally, yes for publishing | Hub display, legal clarity |
| `version` | Yes | Update detection |
| `profile` | Yes | Grouping, profile alignment |
| `aspect` | Yes | Default generation parameter |
| `models` | Yes for legacy compatibility | Backward-compatible model selection and display |
| `providers` | Required for schema v2 multi-provider templates | Provider/model compatibility matrix |
| `capabilities` | Recommended for schema v2 | Runtime routing and filtering |
| `prompt_variants` | Required when more than one model family is listed | Provider-specific prompt block mapping |
| `tags` | Yes (>= 3) | Auto-matching, search |
| `difficulty` | Yes | Filtering |
| `category` | Optional | Hub filtering |
| `samples` | Recommended | Preview and quality proof |
| `created` / `updated` | Yes | Sorting, freshness |

## Type-Specific Body Structure

## `type: prompt`

The body should follow this exact order:

```markdown
## Prompt Template
[code block with {{variable|default}} slots]

## Variables
[pipe table: Variable | Default | Description]

## Tips
[bullet list of specific, actionable tips]
```

Use this type when activation should end in one prompt assembly plus a normal `generate` or `edit`.

## `type: workflow`

The body should follow this exact order:

```markdown
## Goal
[what outcome the workflow should produce]

## When To Use
[when this workflow is a good fit]

## Inputs
[table or bullet list of required/recommended inputs]

## Steps
[numbered execution steps]

## Prompt Blocks
[one or more reusable code blocks the agent can call during the workflow]

## Success Checks
[how to judge whether the workflow output is usable]
```

Use this type when activation should guide the agent through multiple steps, checkpoints, or iterations instead of emitting one assembled prompt immediately.

For iterative workflows, also make these rules explicit when relevant:

- what becomes the `approved_baseline` after a step is accepted
- which `locked_invariants` must remain unchanged later
- what the typical `allowed_delta` looks like for one follow-up round
- which later assets are deterministic derivatives rather than new model generations

## Variable Syntax

`{{name|default}}` — double braces, snake_case name, pipe separator, fallback value.

| Pattern | Meaning |
|---------|---------|
| `{{scene|rain-soaked alley}}` | Variable with default |
| `{{subject}}` | Variable without default |

Rules:

- Names: snake_case, 2-30 chars
- Defaults: complete phrases or sentences
- Prompt templates usually use 3-6 variables
- Workflow templates may use variables inside `## Prompt Blocks`, but they are optional

## Provider-Aware Prompt Variants

Schema v1 templates can keep one `## Prompt Template` block. Schema v2 templates may add provider-specific prompt blocks when model behavior differs materially:

```markdown
## Prompt Template
[generic conservative prompt]

## Prompt Template: gemini
[Gemini/Nano Banana tuned prompt]

## Prompt Template: gpt-image
[GPT Image tuned prompt]
```

Use provider-specific blocks only when they are actually needed. If the generic prompt works across tested models, keep a single block and represent support in `providers`.

Selection is strict:

- The runtime must resolve the effective provider/model first, including aliases such as `nano-banana-pro`.
- If the selected model entry declares `prompt_variant`, use only the matching body block.
- If a matching block is missing, the template is invalid for that model until fixed.
- Do not feed `## Prompt Template: gemini` to GPT Image, or `## Prompt Template: gpt-image` to Gemini/Nano Banana.
- If the selected provider/model is not listed in `providers`, ask before using the neutral prompt or skip the template.

Provider-specific authoring guidance:

- `gemini` / Nano Banana: use descriptive scene language, quote exact labels, state preserved layout/invariants, and avoid SD/MJ quality tags like "8K", "masterpiece", or "ultra-detailed".
- `gpt-image`: state exact constraints, label/text limits, composition requirements, and negative constraints such as no extra labels, no cropped edges, no duplicated parts, and no decorative clutter.
- `chat-image`: treat as best-effort chat response image generation; keep prompts concise and avoid relying on native edit/mask semantics.

## Sample Image Requirements

| Rule | Prompt Template | Workflow Template |
|------|-----------------|-------------------|
| Minimum count | Recommended: >= 1 | Optional during early iteration, recommended for publishing |
| Format | JPG or PNG | JPG or PNG |
| Max size | 2MB per image | 2MB per image |
| Naming | `sample-{model-short}-{nn}.png` | Same |
| Metadata | `file`, `provider`, `model`, `prompt_variant`, `prompt`, `aspect` or `size` | Same if samples exist |
| Mapping | One sample = one exact prompt/model variant | One sample should map to a representative workflow output |

The file name is not cosmetic. It is the fastest way for users and agents to tell which model produced the image when browsing a repo or catalog.

## Iterative Workflow Guidance

When authoring a workflow that includes refinement rounds:

- Prefer one approved baseline over a loose pile of previous attempts
- Each follow-up step should change one major variable at a time
- Prompt blocks for refinement should explicitly say what stays unchanged
- If a later asset is a deterministic derivative, document it as a non-model step instead of phrasing it as another creative generation

## README Requirements

Published/community template repos should include a `README.md` with at least these sections:

```markdown
## Install
## Verified Models
## Supported Models
## License
## Sample Outputs
```

Recommended rule:

- If the repo publishes a workflow template, the README should explain what the workflow does and what the sample represents
- Keep model names exact (`gemini-3-pro-image-preview`, `gpt-image-2`, not just "Pro" or "GPT")

## Validation Command

Run the local validator before publishing or catalog indexing:

```bash
cd bananahub-skill
python3 scripts/validate_templates.py
```

The validator accepts legacy `models` metadata and schema v2 `providers` metadata. It checks required frontmatter fields, provider/model compatibility entries, sample metadata, and type-specific body sections.

## `.source.json` (Install Provenance)

Auto-generated by CLI on install, stored alongside the template:

```json
{
  "repo": "user-a/bananahub-storyboards",
  "ref": "main",
  "sha": "abc123...",
  "installed_at": "2026-03-31T10:00:00Z",
  "version": "1.0.0",
  "cli_version": "0.1.0"
}
```

## `.registry.json` (Local Index)

Auto-generated by scanning installed templates:

```json
{
  "version": "1.0.0",
  "generated_at": "2026-03-31T10:00:00Z",
  "templates": [
    {
      "id": "article-one-page-summary",
      "type": "workflow",
      "title": "文章一图流解读",
      "title_en": "Article One-Page Visual Summary",
      "author": "user-a",
      "profile": "diagram",
      "tags": ["文章解读", "一图流", "article", "summary", "infographic"],
      "difficulty": "intermediate",
      "aspect": "4:3",
      "models": ["gemini-3-pro-image-preview", "gpt-image-2"],
      "providers": ["google-ai-studio", "openai"],
      "provider_matrix": [
        {
          "id": "google-ai-studio",
          "family": "gemini-image",
          "models": [
            {
              "id": "gemini-3-pro-image-preview",
              "aliases": ["nano-banana-pro"],
              "quality": "best",
              "prompt_variant": "gemini"
            }
          ]
        },
        {
          "id": "openai",
          "family": "gpt-image",
          "models": [
            {
              "id": "gpt-image-2",
              "quality": "best",
              "prompt_variant": "gpt-image"
            }
          ]
        }
      ],
      "capabilities": {"generation": true, "edit": false, "mask_edit": false},
      "prompt_variants": {"default": "base", "gemini": "prompt-gemini", "gpt-image": "prompt-gpt-image"},
      "source": "user-a/bananahub-templates",
      "version": "1.0.0",
      "installed_at": "2026-03-31T10:00:00Z"
    }
  ]
}
```

Notes:

- Built-in template registries should not fake install or download counts. Prefer explicit metadata such as `distribution: "bundled"` and `primary_cmd: "/bananahub use <id>"`.
- Installed template registries may include provenance such as `source` and `installed_at`, but popularity metrics belong in the remote BananaHub catalog, not the local registry.
