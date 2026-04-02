# Template System

Nanobanana templates are reusable agent modules. They are not limited to single prompts. A template can be either:

- `type: prompt` — a reusable prompt recipe with variables
- `type: workflow` — a progressive-disclosure playbook that guides the agent through multiple steps

Templates support progressive disclosure: they can be auto-suggested when context matches, or explicitly activated by the user.

## Template Search Paths

Templates are loaded from two locations (merged). On ID conflict, user-installed wins:

1. **Built-in** (shipped with skill): `~/.claude/skills/nanobananaskill/references/templates/`
2. **User-installed** (via `npx bananahub add`): `~/.config/nanobanana/templates/`

Each path contains template directories and an auto-generated `.registry.json` index.

## Discovery Surfaces

- `templates`, `templates <name>`, `use`, and Phase 2.1 auto-matching operate on **installed** templates
- `discover ...` operates on the **remote BananaHub catalog** and should follow `references/hub-discovery.md`

Remote discovery should stay frontmatter-first. Do not load a remote template body until the user chooses a candidate or the shortlist is genuinely ambiguous.

## Template File Format

Templates are agent-consumed `template.md` documents with two layers:

```text
Tier 1 — Frontmatter (always parsed for listing/matching, ~50 tokens)
  id, type, title, profile, tags, models, aspect, difficulty
  → used by: templates list, auto-matching, BananaHub catalog

Tier 2 — Body (loaded only when template is activated via `use`, ~200-600 tokens)
  prompt sections OR workflow sections
  → used by: prompt assembly, guided execution, step-by-step activation
```

## Frontmatter (Tier 1 — Discovery)

Required fields for listing and auto-matching:

| Field | Purpose | Example |
|-------|---------|---------|
| `id` | Unique identifier (lowercase, hyphens, 3-50 chars) | `cyberpunk-city` |
| `type` | Template kind: `prompt` or `workflow` | `workflow` |
| `title` | Chinese display title for listing | `角色一致性分镜工作流` |
| `title_en` | English display title | `Consistent Character Storyboard Workflow` |
| `author` | GitHub username | `nanobanana` |
| `version` | Semver | `1.0.0` |
| `profile` | Target enhancement profile or grouping bucket | `photo` |
| `tags` | Bilingual keywords for search + auto-matching | `[分镜, storyboard, consistency]` |
| `models` | Tested models with quality rating (best/good/ok) | see below |
| `aspect` | Recommended aspect ratio | `"1:1"` |
| `difficulty` | Target user level | `beginner` / `intermediate` / `advanced` |
| `samples` | Optional sample image metadata (file, model, prompt) | see below |
| `created` / `updated` | ISO dates | `2026-03-31` |

Notes:

- Missing `type` should be treated as `prompt` for backward compatibility.
- `workflow` templates may omit sample images during early iteration, but published workflows should still include representative samples when possible.

## Body (Tier 2 — Activation)

The body structure depends on `type`.

### `type: prompt`

Body sections must follow this exact order:

1. **`## Prompt Template`** — the core prompt with `{{variable|default}}` slots inside a code block
2. **`## Variables`** — pipe table mapping each variable to its default and description
3. **`## Tips`** — bullet list of concrete, actionable tips

### `type: workflow`

Body sections should follow this exact order:

1. **`## Goal`** — what outcome this workflow helps the agent produce
2. **`## When To Use`** — scenarios where this workflow is a strong fit
3. **`## Inputs`** — the required or recommended inputs before execution
4. **`## Steps`** — numbered execution steps
5. **`## Prompt Blocks`** — reusable prompt fragments the agent can apply during specific steps
6. **`## Success Checks`** — how to tell the workflow output is good enough to stop or continue

## Body Authoring Constraints

These rules keep templates compact and agent-friendly:

| Rule | Rationale |
|------|-----------|
| **Total body < 140 lines** | Keeps activation cost low |
| **Prompt templates should keep the main prompt < 80 words** | Gemini quality degrades with overly long single-shot prompts |
| **Workflow templates should prefer 4-8 steps** | Too many steps become vague and hard to execute |
| **Variables use snake_case** | Consistent parsing when variables are used |
| **Defaults are complete phrases/sentences** | Gemini understands narrative language better than keyword fragments |
| **No "8K", "ultra-detailed", "masterpiece"** | SD/MJ quality tags do not improve Gemini output |
| **Tips and checks are specific and testable** | Avoid vague advice |
| **Tags include both Chinese and English** | Enables auto-matching from bilingual user input |

## Variable Syntax

`{{name|default_value}}` — double braces, snake_case name, pipe separator, fallback value.

- `{{scene|rain-soaked alley}}` — with default
- `{{subject}}` — without default (must be provided by user)

Prompt templates use this syntax directly in `## Prompt Template`.
Workflow templates may also use it inside `## Prompt Blocks`, but it is optional.

Full format spec: `references/template-format-spec.md`

## `templates` — List All Templates

1. Scan both template search paths for `.registry.json` (or rebuild by scanning directories)
2. Merge results (user-installed wins on ID conflict)
3. Group by `profile`
4. Show both `type` and difficulty in the listing

Example:

```text
Available templates (N)

Photo (photo)
  cyberpunk-city                  [prompt]    ⭐ beginner

General workflows (general)
  consistent-character-storyboard [workflow]  ⭐⭐ intermediate

Usage: /nanobanana templates <name>              Show details
       /nanobanana use <name> [custom description]  Activate template
       /nanobanana create-template               Create a new template
Find more: /nanobanana discover <request>
```

## `discover <request>` — Search BananaHub

1. Read `references/hub-discovery.md`
2. Search the BananaHub machine-readable catalog, not the visual homepage
3. Prefer curated results by default
4. Return a short ranked shortlist with `type`, `profile`, source layer, and `install_cmd`
5. Ask once whether to install the best match, inspect another candidate, or continue without a template
6. If the user approves installation, run `npx bananahub add ...` using the catalog's `install_cmd`
7. After installation, immediately continue with the normal `use <template-id>` flow

## `templates <name>` — Show Template Details

1. Search both template paths for `<name>/template.md`
2. Parse frontmatter and body
3. Display title, type, models, aspect ratio, and tags
4. If `type: prompt`, show the prompt template, variables table, and tips
5. If `type: workflow`, show the goal, inputs, steps, prompt blocks, and success checks
6. If `samples` entries exist in frontmatter, show sample image paths
7. End with usage hint: `/nanobanana use <name>`

## `use <template-id> [custom description]` — Activate Template

1. **Locate template**: search both template paths for `<id>/template.md`
2. **Read frontmatter** and determine `type`
3. **Branch by type**:

### Activation for `type: prompt`

1. Read `## Prompt Template`
2. Extract variables from `{{variable|default}}`
3. Apply user input:
   - If no description is provided, use defaults
   - If a description is provided, map user intent to matching variables and leave the rest unchanged
4. Apply template defaults for `aspect` and best-tested `model` unless the user overrides them
5. Generate using the normal image flow
6. Display template attribution

### Activation for `type: workflow`

1. Read `## Goal`, `## Inputs`, `## Steps`, and `## Prompt Blocks`
2. Treat the workflow as execution context, not as a single prompt
3. Ask only for missing blockers from `## Inputs`
4. If a previous step has an accepted result, mark it as the current approved baseline before continuing
5. Execute one step at a time
6. Use `generate` or `edit` only when a workflow step calls for it
7. Preserve state from the last accepted step instead of restarting from scratch
8. For follow-up edits, explicitly state the locked invariants and the one allowed delta for the current round
9. If a later step is a deterministic derivative rather than a creative reinterpretation, prefer a local deterministic transform instead of re-calling the model
10. Stop after each meaningful milestone if the user wants to review before continuing

For workflow activation, `use <template-id>` means "start or continue this guided workflow", not "immediately fire one prompt".

## Template Variable Resolution

When matching user descriptions to prompt-template variables:

1. **Direct mapping**: if user mentions a concept that clearly maps to a variable, replace it
2. **Partial override**: only replace the variables the user mentioned
3. **Full override**: if the user provides a scene that does not map cleanly to variables, treat the template as a starting scaffold rather than a hard wrapper
4. **Conflict resolution**: the user's explicit choices override template defaults

For workflow templates, variable resolution is optional. Prefer using the workflow steps and prompt blocks directly unless a block clearly defines variables.

## `create-template` — AI-Guided Template Creation

When the user invokes `create-template`, guide them through creating either a prompt template or a workflow template.

### Phase 1: Choose Template Type

Ask early:

1. "你要做的是单步 prompt 模板，还是多步 workflow 模板？"
2. If unclear, infer from the task:
   - Stable reusable shot/prompt structure → `prompt`
   - Guided SOP, multi-step iteration, stateful process → `workflow`

### Phase 2: Intent Gathering

Ask the user:

1. "这个模板主要解决什么问题？" → determine goal
2. "更像单步生成还是多步流程？" → confirm type if still unclear
3. "适用于什么图片类型？" → determine profile
4. "哪些输入必须提供，哪些可以默认？" → identify variables or workflow inputs
5. "目标用户是谁？新手还是有经验的？" → difficulty
6. If the template is iterative: "一旦某一版被接受，哪些元素必须完全不变？每轮只允许改什么？" → determine baseline-lock and allowed-delta rules

### Phase 3: Draft the Body

For `type: prompt`:

1. Draft a compact English prompt template
2. Insert `{{variable|default}}` slots
3. Add variables and tips

For `type: workflow`:

1. Draft the workflow goal and when-to-use section
2. List the required inputs
3. Write the numbered steps
4. Add a baseline-lock step when the workflow includes refinement rounds
5. Add prompt blocks for the steps that call Gemini
6. Distinguish creative edit steps from deterministic derivative steps when relevant
7. Add success checks

### Phase 4: Sample Generation and Assembly

1. Generate 2-3 representative outputs when practical
2. Save chosen samples with model-explicit names such as `sample-3-pro-01.png`
3. Record sample metadata in frontmatter
4. Ask for `id`, `title`, `title_en`, and bilingual `tags`
5. Assemble `template.md` and `README.md`
6. Validate the result against the type-aware template rules

## Template Validation Rules

| Check | `prompt` | `workflow` |
|-------|----------|------------|
| `type` | `prompt` or omitted | `workflow` |
| Core sections | `Prompt Template`, `Variables`, `Tips` | `Goal`, `Inputs`, `Steps`, `Prompt Blocks` |
| Variables | Recommended, usually 3-6 | Optional |
| Prompt length | Main prompt < 80 words | Prompt blocks should stay concise |
| Steps | Optional | Recommended numbered list |
| Samples | Strongly recommended | Recommended but may be omitted during early iteration |
| README | Recommended for publishing | Recommended for publishing |
