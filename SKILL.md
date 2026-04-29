---
name: bananahub
description: >
  Agent-native multi-provider image workflow for `/bananahub`. Normalizes non-English prompts into English by default,
  generates or edits images across Gemini/Nano Banana, OpenAI GPT Image, and chat-compatible image routes, and discovers or uses
  BananaHub prompt and workflow templates. Trigger only when the user explicitly mentions
  bananahub / BananaHub or uses the `/bananahub` command. Do NOT activate on generic image-generation
  requests like "生成图片" or "画一个".
  Typical triggers: "/bananahub", "用 bananahub 画", "bananahub 生图", "bananahub 优化提示词",
  "bananahub 找模板", and "/bananahub discover".
metadata:
  version: 0.1.0
  author: bananahub-ai
  emoji: 🍌
  requires:
    bins:
      - python3
    python:
      - google-genai
      - pillow
    env:
      - GEMINI_API_KEY
      - GOOGLE_API_KEY
  primaryEnv: GEMINI_API_KEY
user_invocable: true
---

# BananaHub

Generate or edit provider-backed images from non-English or mixed-language requests inside one `/bananahub` workflow. Gemini/Nano Banana remains the default model family, and OpenAI GPT Image support is provider-routed. BananaHub keeps prompt optimization, conservative enhancement, model fallback, image editing, template use, and BananaHub discovery in a single skill instead of splitting them across separate installs.

## Quick Start

- Install via Open Agent Skills: `npx skills add https://github.com/bananahub-ai/bananahub-skill --skill bananahub`
- Install in Claude Code directly: `claude skill install https://github.com/bananahub-ai/bananahub-skill`
- Run setup once: `/bananahub init`
- Generate from a natural-language request: `/bananahub 一只橘猫趴在键盘上打盹`
- Edit an image: `/bananahub edit 把背景换成海滩 --input photo.png`
- Discover a reusable template: `/bananahub discover 代码库讲解图`

## Key Paths

- **Generation script**: `{baseDir}/scripts/bananahub.py`
- **Provider adapters**: `{baseDir}/scripts/providers/` — Gemini, OpenAI Images, and chat/completions-compatible runtime adapters
- **Runtime config module**: `{baseDir}/scripts/runtime_config.py` — provider constants, aliases, transport defaults, config keys, and endpoint normalization
- **Config store module**: `{baseDir}/scripts/config_store.py` — config loading, profile merge, validation, provider override, and serialization helpers
- **Prompt optimization rules**: `references/prompt-guide.md` — read during Phase 1 (base optimization)
- **Enhancement profiles**: `references/profiles/{name}.md` — read during Phase 3 (on-demand)
- **Official references**: `references/official-sources.md` — authoritative source URLs, core example library
- **Capability registry**: `references/capability-registry.md` — provider/model feature routing and fallback policy
- **Model registry**: `references/model-registry.json` — canonical model ids, aliases, defaults, and provider families
- **Provider guides**: `references/providers/{provider}.md` — lazy-loaded model-family prompt and runtime rules
- **Template system**: `references/template-system.md` — read when handling templates/use/create-template commands
- **Hub discovery guide**: `references/hub-discovery.md` — read when handling `discover` or when local template matching is weak
- **Template files**: `{baseDir}/references/templates/<id>/template.md` (built-in) + `~/.config/bananahub/templates/<id>/template.md` (user-installed)
- **Telemetry helper**: `python3 {baseDir}/scripts/bananahub.py telemetry ...` — use for built-in/installed template adoption events
- **Telemetry state**: `~/.config/bananahub/telemetry.json` — stores the local anonymous usage id
- **Init guide**: `references/init-guide.md` — read when handling `init` command
- **Optimization pipeline**: `references/optimization-pipeline.md` — read when optimizing prompts
- **Template format spec**: `references/template-format-spec.md` — detailed field definitions, repo structure, sample requirements
- **Template validator**: `python3 {baseDir}/scripts/validate_templates.py` — validates bundled/user template metadata for schema v1/v2 compatibility
- **Mode detector**: `python3 {baseDir}/scripts/bananahub.py check-mode` — reports provider-backed / host-native / prompt-only execution mode and capability layer boundaries
- **Prompt archive**: current working directory `bananahub-prompts/` when `--save-prompt`, `--prompt-output`, or `BANANAHUB_SAVE_PROMPTS=1` is used
- **API config** (priority high→low):
  1. `--config <file>` CLI flag
  2. Environment variables (`GOOGLE_API_KEY`, `GEMINI_API_KEY`, `BANANAHUB_PROVIDER`, `BANANAHUB_AUTH_MODE`, `BANANAHUB_MODEL`, `GOOGLE_GEMINI_BASE_URL`, `GEMINI_BASE_URL`, `BANANAHUB_BASE_URL`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`)
  3. Skill config: `~/.config/bananahub/config.json`
     - `{"provider": "google-ai-studio", "api_key": "...", "model": "gemini-3-pro-image-preview"}`
     - `{"provider": "gemini-compatible", "api_key": "...", "base_url": "https://..."}`
     - `{"provider": "openai", "openai_api_key": "...", "model": "gpt-image-2"}`
     - `{"provider": "openai-compatible", "api_key": "...", "base_url": "https://...", "model": "gpt-image-2"}`
     - `{"provider": "chatgpt-compatible", "chatgpt_api_key": "...", "chatgpt_base_url": "https://...", "model": "gpt-5.4"}`
     - multi-profile: `{"default_profile":"nano","profiles":{"nano":{"provider":"google-ai-studio","api_key":"..."},"gpt":{"provider":"openai","openai_api_key":"...","model":"gpt-image-2"}}}`
     - `{"provider": "vertex-ai", "auth_mode": "adc", "project": "...", "location": "global"}`
  4. Persistent config helpers:
     - `python3 {baseDir}/scripts/bananahub.py config show`
     - `python3 {baseDir}/scripts/bananahub.py config set --provider google-ai-studio --api-key <key>`
     - `python3 {baseDir}/scripts/bananahub.py config set --provider gemini-compatible --base-url https://your-gemini-compatible-endpoint --api-key <key>`
     - `python3 {baseDir}/scripts/bananahub.py config set --provider openai-compatible --base-url https://your-openai-compatible-endpoint --api-key <key>`
     - `python3 {baseDir}/scripts/bananahub.py config set --provider vertex-ai --auth-mode adc --project <gcp-project> --location global`
     - `python3 {baseDir}/scripts/bananahub.py config set --model gemini-3.1-flash-image-preview`
     - `python3 {baseDir}/scripts/bananahub.py config set --clear-base-url`
- **Output directory**: current working directory (where the skill is invoked)

## First-Run Detection

Before executing any command other than `help`, check if the environment is ready:
1. Check whether **any supported config source** exists (CLI flag, env vars, config.json, .env)
2. If not → inform the user and automatically start the init flow (read `references/init-guide.md`)
3. If config exists but a generation command fails with auth/dependency errors → suggest running `init`
4. Persist new config into `~/.config/bananahub/config.json`
5. Treat `google-ai-studio` as the default provider
6. Supported runtime providers:
   - `google-ai-studio`: generate / edit / models / init
   - `gemini-compatible`: generate / edit / models / init
   - `vertex-ai`: generate / edit / models / init
   - `openai`: OpenAI-native GPT Image generate / edit / models / init
   - `openai-compatible`: OpenAI-style endpoint generate / models / init, capability-dependent
   - `chatgpt-compatible`: chat/completions endpoint that returns images inside assistant replies
7. `openai-compatible` is not the same as OpenAI-native GPT Image. Do not assume edit, mask edit, or GPT Image parameters unless the endpoint declares support.
8. Endpoint normalization rules:
   - `gemini-compatible`: if the user pastes a URL ending in `/v1beta`, keep it conceptually but normalize the trailing version during runtime so it is not duplicated
   - `openai-compatible`: if the user pastes a bare host, the runtime may append `/v1`; for Google's official endpoint, resolve it to `/v1beta/openai`

## Runtime Mode Layers

Run `python3 {baseDir}/scripts/bananahub.py check-mode --pretty` when the execution path is unclear. BananaHub has three execution modes:

| Mode | Trigger | Behavior |
|---|---|---|
| `provider-backed` | Config validates for a supported provider | Optimize/render prompt, call `generate` or `edit`, and save image outputs |
| `host-native` | Provider config is missing or incomplete, but `BANANAHUB_HOST_IMAGEGEN=1` or the caller explicitly has a native image tool | Optimize/render prompt, optionally archive it, then hand it to the host image tool instead of calling the provider script |
| `prompt-only` | No valid provider and no host image tool | Act as a prompt/template advisor: return the final prompt and archive it when requested; do not claim image generation succeeded |

Capability ownership is layered:

- **Cross-model skill layer**: prompt optimization, translation policy, conservative enhancement, `--direct`, `--raw`, prompt archiving, template discovery/activation, host-native delegation, and prompt-only advisory output.
- **Template layer**: matching and activation are common, but provider/model compatibility, prompt variants, tested quality, and samples belong to template metadata.
- **Provider/model layer**: image edit, mask edit, multi-reference, exact size, native quality, transparent background, output format/compression, and fallback are not universal; route them through `references/capability-registry.md`, `references/model-registry.json`, and provider adapters.

If a feature changes request payload shape, file validation, cost, policy behavior, or output parsing, do not treat it as cross-model even if several providers happen to support similar wording.

## Command Routing

Route user input to the appropriate action based on arguments:

| Argument | Action |
|---|---|
| `init` | Read `references/init-guide.md`, then diagnose and fix environment issues |
| `help` | Show usage instructions (brief list of supported commands and examples) |
| `<description>` | Read `references/optimization-pipeline.md`, then: base optimization → intent recognition → optional enhancement → generate |
| `edit <description> --input <image-path> [--ref <reference-image>...]` | Edit an existing image: optimize prompt → call edit subcommand |
| `optimize <description>` | Optimize prompt only; display result without generating |
| `generate <English prompt>` | Generate image directly with given English prompt (skip optimization) |
| `models` | Run `python3 {baseDir}/scripts/bananahub.py models` to query image-capable models from API |
| `check-mode` | Run `python3 {baseDir}/scripts/bananahub.py check-mode --pretty` to inspect provider-backed / host-native / prompt-only mode and capability layers |
| `templates` | Read `references/template-system.md`, then list all templates grouped by profile and type |
| `templates <name>` | Read `references/template-system.md`, parse frontmatter `type`, then show prompt-template or workflow-template details accordingly |
| `use <template-id> [custom description]` | Read `references/template-system.md`, parse frontmatter `type`, then either generate from a prompt template or activate a workflow template |
| `discover <request>` | Read `references/hub-discovery.md`, then search BananaHub for matching templates without scraping the visual site |
| `discover curated <request>` | Read `references/hub-discovery.md`, then search only the curated BananaHub catalog |
| `discover trending` | Read `references/hub-discovery.md`, then show current trending BananaHub templates |
| `create-template [description]` | Read `references/template-system.md`, determine whether the user needs a prompt or workflow template, then guide creation |

Note:
- `optimize`, `--direct`, and `--raw` are **skill-layer controls** interpreted by you before invoking the script
- Do **not** pass `--direct` or `--raw` through to `{baseDir}/scripts/bananahub.py`
- `discover` is also a **skill-layer command**: use BananaHub machine-readable files and `npx bananahub add ...`, not `{baseDir}/scripts/bananahub.py`
- `telemetry` is an **internal helper**, not a user-facing chat command. Use it when a template is selected or successfully produces output.

Optional flags (append to any generation command):
- `--model <model_id>` — specify model
- `--aspect <ratio>` — aspect ratio (e.g., 16:9, 1:1, 9:16)
- `--image-size <preset>` — native image-size preset (`1K`, `2K`, `4K`)
- `--openai-size <value>` — OpenAI-native size for OpenAI-style image generation
- `--quality <value>` — provider-native quality preset when supported
- `--background <value>` — provider-native background option when supported
- `--output-format <value>` — provider-native output format when supported
- `--output-compression <N>` — provider-native output compression when supported
- `--resize <WxH>` — post-process resize after generation/edit (e.g., `1024x1024`)
- `--size <value>` — legacy compatibility flag; `1K/2K/4K` means native image size, `WxH` means post-process resize
- `--output <path>` — specify output path
- `--save-prompt` — archive the final prompt under `bananahub-prompts/`
- `--prompt-output <path>` — archive the final prompt to a specific file or directory
- `--input <path>` — source image for edit commands
- `--ref <path> [path...]` — reference images for edit commands (Gemini up to 13 refs; OpenAI provider enforces its own lower runtime limit)
- `--mask <path>` — OpenAI-native mask image for masked edits
- `--direct` — direct mode: skip all confirmations, generate immediately
- `--raw` — raw mode: translate only, no optimization
- `--retries <N>` — retry count per model on 503 before fallback (default: 1, i.e. try each model twice)
- `--no-fallback` — disable automatic model fallback

## Three Optimization Modes

### Mode 1: Default (no flag)
```
User input → Base optimization (silent) → Intent recognition → Profile match?
  ├─ Yes → Show enhancement suggestion → User confirms/edits/rejects → Generate
  └─ No (general) → Generate directly
```

### Mode 2: Direct (`--direct` or user says "直接画/直出")
```
User input → Base optimization → Intent recognition → Load Profile enhancement → Generate directly
```
No confirmations. Suitable for experienced users or batch generation.

### Mode 3: Raw (`--raw`)
```
User input → Translate to English only → Generate directly
```
No optimization. In-image text is still preserved in original language.

## Prompt Optimization Summary

Read `references/optimization-pipeline.md` for the full pipeline. Overview:

1. **Phase 0**: Extract hard constraints (exact_text, must_keep, must_avoid, style_lock, approved_baseline, allowed_delta when relevant)
2. **Phase 1**: Base optimization — format correction, smart translation, structuring, conservative guardrail
3. **Phase 1.5**: Capability/provider routing — inspect `references/capability-registry.md`, resolve model aliases from `references/model-registry.json`, then lazy-load `references/providers/*.md` only for the selected model family
4. **Phase 2**: Intent recognition — match to one of 10 profiles via keyword table
4. **Phase 2.1**: Local template auto-matching — suggest installed templates (progressive disclosure)
5. **Phase 2.2**: BananaHub discovery — search remote catalog only when explicitly useful
6. **Phase 2.5**: Style overlay detection (hand-drawn sketch-note)
7. **Phase 3**: Enhancement — read matching profile from `references/profiles/`, classify subject, fill missing dimensions
8. **Phase 3.5**: Model recommendation — prefer `gpt-image-2` for generation-led high-fidelity outputs; prefer Gemini/Nano Banana for edit/reference/consistency-heavy flows unless the user or template overrides it

## Image Generation Flow

1. Build command:
   ```bash
   python3 {baseDir}/scripts/bananahub.py generate "<prompt>" [--aspect RATIO] [--model MODEL] [--output PATH]
   ```
   When this generation comes from an active template, also pass:
   `--template-id <id> --template-repo <repo> --template-distribution bundled|remote --template-source curated|discovered`
2. Execute script and parse JSON output
3. **Automatic model fallback**: on server error (500/502/503/504), tries the selected provider family fallback chain from `references/model-registry.json`. Do not cross provider families unless the user explicitly enables cross-provider fallback. Use `--no-fallback` to disable.
4. On success:
   ```
   ✅ 图片已生成
   📁 路径: [file_path]
   🔧 模型: [model] | 宽高比: [ratio] | 尺寸: [WxH]
   📝 使用的 Prompt: [final prompt used]
   ```
   If the script returns `template_telemetry`, treat it as best-effort success reporting only; do not surface failures unless the user asked.
5. On failure: suggest fix based on error type (content policy → rephrase, auth → check key, network → check proxy)

## Image Editing Flow

1. **Validate input**: confirm `--input` image path exists; validate `--ref` images
   Reject more than 13 reference images or more than 14 total images.
2. **Extract invariants**: what must remain unchanged in the source image
3. **Lock the baseline when applicable**: if the source image is an accepted result, treat it as the only source of truth for later rounds
4. **Name the allowed delta**: isolate the one change this round is allowed to make
5. **Optimize edit prompt**: run Phase 1 only (skip Phase 2/3); keep conservative, isolate the delta
6. **Build command**:
   ```bash
   python3 {baseDir}/scripts/bananahub.py edit "<prompt>" --input <image_path> [--ref <ref1> ...] [--model MODEL] [--output PATH]
   ```
   `--ref` accepts up to 13 reference images. Total images (input + refs) ≤ 14.
   When this edit runs inside an active template/workflow, also pass:
   `--template-id <id> --template-repo <repo> --template-distribution bundled|remote --template-source curated|discovered`
7. On success:
   ```
   ✅ 图片已编辑
   📁 路径: [file_path]
   📥 原图: [input_path]
   📎 参考图: [ref_images, if any]
   🔧 模型: [model] | 尺寸: [WxH]
   📝 使用的 Prompt: [final prompt used]
   ```

Multi-image use cases: style transfer, character consistency, multi-image blending, object replacement.

## Iteration Guide

- Change one variable at a time
- Retain the last effective prompt as a base
- Treat follow-ups as deltas, not full rewrites
- Preserve locked constraints unless user explicitly changes them
- After the user accepts an output, treat that file as the approved baseline until the user replaces it
- For follow-up edits, state the exact keep-unchanged constraints before the allowed delta
- For deterministic derivative tasks such as invert, crop, export, add safe padding, or build exact lockups, prefer local deterministic transforms instead of asking the model to redraw the asset

## Template System Summary

Read `references/template-system.md` for the full template system. Overview:

- **Search paths**: built-in (`references/templates/`) + user-installed (`~/.config/bananahub/templates/`)
- **Local vs remote**: `templates` / `use` operate on installed templates; `discover` operates on BananaHub catalog, including the official `bananahub-ai/templates` library, and installs only on demand
- **Format**: `template.md` with YAML frontmatter and `type: prompt | workflow`
- **Prompt templates**: produce a reusable prompt with variables, then generate or edit
- **Workflow templates**: act as progressive-disclosure context; load the workflow, ask only for missing blockers, and execute step-by-step with `generate` / `edit` primitives when needed
- **Model transparency**: when a template or heuristic selects `gpt-image-2` or Gemini/Nano Banana automatically, state that recommendation explicitly instead of hiding the model choice
- **Built-in starter examples**: `info-diagram` for one-page infographics, `article-one-page-summary` for article explainers, `background-replace-edit` for edit workflows
- **Commands**: `templates` (list installed), `templates <name>` (details), `use <id> [desc]` (activate), `discover <need>` (search hub), `create-template` (create)
- **Auto-matching**: Phase 2.1 suggests installed templates first; Phase 2.2 can search BananaHub when local coverage is weak
- **Adoption telemetry**: when a template is selected, call `python3 {baseDir}/scripts/bananahub.py telemetry track --event selected ...`; when template-driven `generate`/`edit` succeeds, pass template telemetry flags so the script can report `generate_success` / `edit_success`
- **Install more**: prefer `discover` inside the skill; official rich templates install from `bananahub-ai/templates`, and known targets can still be installed with `npx bananahub add <user/repo[/template]>`
- **Publishing rule**: when creating templates, save samples as `sample-{model-short}-{nn}.png` and make README list verified models, supported models, and sample-to-prompt mappings

## Safety Rules

- Never generate images that violate content policies (violence, sexual content, hate, etc.)
- Never expose the API key in output
- If a user request might trigger safety filters, proactively suggest alternative phrasing
