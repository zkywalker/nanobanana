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
├── cyberpunk-city/
│   ├── template.md
│   └── samples/
├── consistent-character-storyboard/
│   ├── template.md
│   └── samples/
└── README.md
```

**`bananahub.json`** (multi-template repo manifest):

```json
{
  "type": "multi",
  "templates": ["cyberpunk-city", "consistent-character-storyboard"]
}
```

## `template.md` Complete Field Reference

```yaml
---
# === Identity ===
id: consistent-character-storyboard      # Unique ID (lowercase, hyphens, 3-50 chars)
type: workflow                           # prompt | workflow
title: 角色一致性分镜工作流
title_en: Consistent Character Storyboard Workflow
description: 多步角色一致性分镜工作流      # Optional short description
author: github-username
version: 1.0.0

# === Generation Config ===
profile: general
aspect: "1:1"
models:
  - name: gemini-3-pro-image-preview
    quality: best
  - name: gemini-3.1-flash-image-preview
    quality: good

# === Discovery ===
tags: [分镜, 故事板, storyboard, consistency]
difficulty: intermediate
category: art

# === Sample Images ===
samples: []                              # Prompt templates should usually provide samples

# === Metadata ===
created: 2026-03-31
updated: 2026-03-31
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
| `version` | Yes | Update detection |
| `profile` | Yes | Grouping, profile alignment |
| `aspect` | Yes | Default generation parameter |
| `models` | Yes (>= 1) | Model selection, display |
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

## Sample Image Requirements

| Rule | Prompt Template | Workflow Template |
|------|-----------------|-------------------|
| Minimum count | Recommended: >= 1 | Optional during early iteration, recommended for publishing |
| Format | JPG or PNG | JPG or PNG |
| Max size | 2MB per image | 2MB per image |
| Naming | `sample-{model-short}-{nn}.png` | Same |
| Metadata | `file`, `model`, `prompt`, `aspect` | Same if samples exist |
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
## Sample Outputs
```

Recommended rule:

- If the repo publishes a workflow template, the README should explain what the workflow does and what the sample represents
- Keep model names exact (`gemini-3-pro-image-preview`, not just "Pro")

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
      "id": "consistent-character-storyboard",
      "type": "workflow",
      "title": "角色一致性分镜工作流",
      "title_en": "Consistent Character Storyboard Workflow",
      "author": "user-a",
      "profile": "general",
      "tags": ["分镜", "storyboard", "consistency"],
      "difficulty": "intermediate",
      "aspect": "1:1",
      "models": ["gemini-3-pro-image-preview"],
      "source": "user-a/bananahub-storyboards",
      "version": "1.0.0",
      "installed_at": "2026-03-31T10:00:00Z"
    }
  ]
}
```
