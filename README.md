# BananaHub Skill 🍌

[简体中文说明](./README.zh-CN.md)

A skill for Gemini image generation and editing that can normalize non-English image requests into optimized English prompts by default, then generate or edit images from the same `/bananahub` entry point.

## Quick Start

```bash
# Open Agent Skills / skills.sh
npx skills add https://github.com/bananahub-ai/bananahub-skill --skill bananahub

# Or install directly in Claude Code
claude skill install https://github.com/bananahub-ai/bananahub-skill

/bananahub init
/bananahub 一只橘猫趴在键盘上打盹
```

## Why BananaHub

BananaHub is one installable skill that keeps the whole Gemini image workflow together:

- **One command surface** — optimize, generate, edit, iterate, use templates, and discover more from `/bananahub`
- **Progressive disclosure guidance** — low-risk cleanup stays quiet; the skill only asks when ambiguity would materially change the result
- **Reusable template ecosystem** — built-ins cover common jobs, while BananaHub lets users discover and install extra prompt or workflow modules without splitting the base skill into multiple SKUs

BananaHub's prompt and workflow design is distilled from official Google / Gemini image-generation docs, prompt guides, and public best practices, then adapted into a constraint-first, agent-native workflow. See [official source references](references/official-sources.md).

## What It Does

1. **Smart prompt optimization** — Translates non-English descriptions into high-quality English prompts by default, fixing common issues (keyword dumps, SD/MJ syntax, negative phrasing, etc.)
2. **Conservative intent-aware enhancement** — Detects image intent (photo, illustration, diagram, text-heavy, minimal, sticker, 3D, product, concept-art) and applies domain-specific enhancements without inventing unnecessary style decisions
3. **In-image text preservation** — Keeps source-language text meant to appear in the image (e.g. `写着"生日快乐"的蛋糕` → `a cake with the text "生日快乐"`)
4. **Constraint-first workflow** — Extracts exact text, keep/avoid constraints, target use, and edit invariants before generating
5. **Multiple generation modes** — Default (interactive), Direct (no confirmations), and Raw (translate-only)
6. **Template-driven reuse and distribution** — Uses built-in templates, supports AI-guided template creation, and connects to BananaHub for searchable installation

## Design Principles

- **Ask instead of guess** when multiple plausible directions would materially change the result
- **Do not add high-impact details lightly**: background, palette, lighting mood, lens language, texture, extra props
- **Treat text and structure as locked content** for posters, logos, diagrams, and information graphics
- **Standardize the final prompt in English by default** for consistency; preserve original language only for in-image text and locked names/labels
- **For edits, preserve invariants first** and change only the requested delta
- **Iterate one major variable at a time** for follow-up revisions

## Installation

```bash
npx skills add https://github.com/bananahub-ai/bananahub-skill --skill bananahub

# or install directly in Claude Code
claude skill install https://github.com/bananahub-ai/bananahub-skill
```

Primary command: `/bananahub`

Compatibility notes:
- Preferred persistent config now lives at `~/.config/bananahub/config.json`.

## Setup

After installation, run the init command to configure your environment:

```
/bananahub init
```

This setup flow will:
- Check Python dependencies (`google-genai`, `pillow`)
- Guide you through choosing a provider path and writing the matching config
- Test API connectivity once the basics are ready

If you prefer to preinstall dependencies manually:

```bash
python3 -m pip install --user google-genai pillow
```

Persistent config helpers:

```bash
# Show effective config resolution
python3 scripts/bananahub.py config show

# Google AI Studio / Gemini Developer API
python3 scripts/bananahub.py config set --provider google-ai-studio --api-key <your_api_key>

# Gemini-compatible relay / proxy
python3 scripts/bananahub.py config set --provider gemini-compatible --base-url https://your-gemini-compatible-endpoint --api-key <your_proxy_key>

# OpenAI-compatible endpoint
python3 scripts/bananahub.py config set --provider openai-compatible --base-url https://your-openai-compatible-endpoint --api-key <your_api_key>

# Vertex AI
python3 scripts/bananahub.py config set --provider vertex-ai --auth-mode adc --project <gcp-project> --location global

# Optional: persist a default model
python3 scripts/bananahub.py config set --model gemini-3.1-flash-image-preview

# Clear the stored custom endpoint and go back to Google's default endpoint
python3 scripts/bananahub.py config set --clear-base-url
```

BananaHub now supports 4 provider paths:

- `google-ai-studio`: recommended default, supports `generate / edit / models / init`
- `gemini-compatible`: Gemini-style relays/proxies, supports `generate / edit / models / init`
- `vertex-ai`: enterprise / GCP path, supports `generate / edit / models / init`
- `openai-compatible`: OpenAI-style gateways, currently supports `generate / models / init`

`openai-compatible` does not support `edit` in the current runtime. Use `google-ai-studio`, `gemini-compatible`, or `vertex-ai` for image editing.

For third-party `base_url` inputs:

- `gemini-compatible`: you can paste either the provider root or a URL that already ends in `/v1beta`; BananaHub normalizes the trailing API version so it does not get duplicated
- `openai-compatible`: if you provide a bare host, BananaHub will try to append `/v1`; for Google's official OpenAI-compatible endpoint it will resolve to `https://generativelanguage.googleapis.com/v1beta/openai`
- If the provider docs already give a full endpoint path, prefer pasting it verbatim

You can provide these settings through `~/.config/bananahub/config.json` or environment variables such as `GOOGLE_API_KEY`, `GEMINI_API_KEY`, `BANANAHUB_PROVIDER`, `BANANAHUB_AUTH_MODE`, `BANANAHUB_MODEL`, `GOOGLE_GEMINI_BASE_URL`, `GEMINI_BASE_URL`, `BANANAHUB_BASE_URL`, `GOOGLE_CLOUD_PROJECT`, and `GOOGLE_CLOUD_LOCATION`.

**Create/manage your Gemini API key**: https://aistudio.google.com/apikey

Check the current official pricing/quota policy here:
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/rate-limits

## Template Usage Telemetry

BananaHub now separates template distribution from template adoption:

- **Remote templates** still use install counts
- **Built-in templates** use usage telemetry instead of fake install counts

The local runtime keeps a best-effort anonymous id in `~/.config/bananahub/telemetry.json` and reports:

- `selected` — the template was chosen for activation
- `generate_success` — a template-driven generation finished successfully
- `edit_success` — a template-driven edit finished successfully

Check local telemetry state:

```bash
python3 scripts/bananahub.py telemetry status
```

Disable telemetry for a run or shell session:

```bash
export BANANAHUB_DISABLE_TELEMETRY=1
```

## Usage

```
/bananahub 一只橘猫趴在键盘上打盹
```

### Commands

| Command | Description |
|---|---|
| `/bananahub <description>` | Optimize prompt + generate image |
| `/bananahub edit <描述> --input <图片>` | Edit an existing image with a text prompt |
| `/bananahub optimize <描述>` | Optimize prompt only (no generation) |
| `/bananahub generate <English prompt>` | Generate with an English prompt directly |
| `/bananahub models` | List available models |
| `/bananahub discover <need>` | Search BananaHub for matching templates and suggest install candidates |
| `/bananahub discover trending` | Show current trending BananaHub templates |
| `/bananahub init` | Check/setup environment |
| `/bananahub help` | Show usage instructions |

### Flags

| Flag | Description |
|---|---|
| `--direct` | Skill-layer mode: skip confirmations, but still keep enhancement conservative |
| `--raw` | Skill-layer mode: translate only, no optimization |
| `--model <id>` | Specify model (`gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview`, or `gemini-2.5-flash-image`) |
| `--aspect <ratio>` | Aspect ratio (e.g. `16:9`, `1:1`, `9:16`) |
| `--image-size <preset>` | Native image-size preset (`1K`, `2K`, `4K`) |
| `--resize <WxH>` | Post-process resize after generation/edit |
| `--size <value>` | Legacy compatibility flag: `1K/2K/4K` means native image size, `WxH` means post-process resize |
| `--output <path>` | Custom output file path |
| `--input <path>` | Source image for edit commands |

### Examples

```bash
# Basic usage — interactive optimization
/bananahub 赛博朋克风格的东京街头夜景

# Direct mode — no confirmations
/bananahub 水彩风格的猫咪 --direct

# Raw mode — translate only, no optimization
/bananahub 一个简单的红色圆圈 --raw

# Specify aspect ratio, model, and native image size
/bananahub 山水画风格的桂林风景 --aspect 16:9 --model gemini-2.5-flash-image --image-size 2K

# Sticker / emoji
/bananahub 画一个开心的柴犬表情包

# 3D render
/bananahub 等距视角的咖啡店室内设计

# Product photography
/bananahub 白底蓝牙耳机产品图

# Concept art
/bananahub 赛博朋克风格的女性角色设计

# Edit an existing image
/bananahub edit 把背景换成海滩 --input photo.png

# Edit with native 2K output, then resize for delivery
/bananahub edit 添加一顶圣诞帽 --input avatar.png --image-size 2K --resize 1024x1024 --output avatar_xmas.png
```

## Templates

Built-in templates are reusable agent modules. Some are `prompt` templates that assemble one reusable prompt. Others are `workflow` templates that load a guided multi-step playbook. Use them directly, override only the pieces you care about, or install more from BananaHub when a repeatable job deserves its own module.

### Template Commands

| Command | Description |
|---|---|
| `/bananahub templates` | List all available templates |
| `/bananahub templates <name>` | Show template details based on its type |
| `/bananahub use <name>` | Activate a prompt template or start a workflow template |
| `/bananahub use <name> <描述>` | Activate with custom variable overrides or workflow context |
| `/bananahub discover <need>` | Search BananaHub and recommend remote templates |
| `/bananahub create-template` | AI-guided prompt/workflow template creation wizard |

### Examples

```bash
# List all templates
/bananahub templates

# Preview a template
/bananahub templates cyberpunk-city

# Generate with prompt-template defaults
/bananahub use cyberpunk-city

# Override prompt-template variables with a description
/bananahub use cyberpunk-city 东京新宿街头，紫色和金色霓虹

# Start a workflow template
/bananahub use consistent-character-storyboard

# Plan section visuals for an article or tutorial
/bananahub use article-illustration-workflow docs/guide.md

# Ask the skill to search BananaHub for a matching workflow
/bananahub discover logo 品牌标识

# Use with flags
/bananahub use cyberpunk-city 上海外滩未来版 --aspect 9:16
```

### Workflow Spotlight

`consistent-character-storyboard` is the built-in example of a multi-step workflow template. It is meant for character-consistency storyboard exploration rather than one-shot final art.

Typical flow:

```bash
# Step 1: create or approve one master reference
/bananahub 一个可爱的暹罗猫IP，奶油色毛发，深棕色重点色，蓝眼睛，戴青绿色小围巾和金色铃铛

# Step 2: start the workflow template
/bananahub use consistent-character-storyboard
```

### Built-in Templates

| ID | Type | Title | Profile |
|---|---|---|---|
| `cyberpunk-city` | prompt | 赛博朋克城市夜景 | photo |
| `cute-sticker` | prompt | Q版贴纸表情包 | sticker |
| `product-white-bg` | prompt | 电商白底产品图 | product |
| `info-diagram` | prompt | 信息图/流程图 | diagram |
| `minimal-wallpaper` | prompt | 极简手机壁纸 | minimal |
| `consistent-character-storyboard` | workflow | 角色一致性分镜工作流 | general |
| `repo-explainer-diagram` | workflow | 代码库讲解图工作流 | diagram |
| `readme-launch-visual` | workflow | README 启动视觉工作流 | text-heavy |
| `article-illustration-workflow` | workflow | 文章配图工作流 | diagram |
| `asset-style-consistency-pack` | workflow | 本地素材风格统一工作流 | general |

### Installing More Templates (BananaHub)

Use `/bananahub discover <need>` when you want the skill to search BananaHub for you, rank a few candidates, and continue directly into installation and activation.

```bash
# Ask the skill to search BananaHub
/bananahub discover repository explainer diagram

# Search the hub directly from the CLI
npx bananahub search <keyword>

# Install a template from GitHub when the install target is already known
npx bananahub add <username>/<repo>
```

User-installed templates are stored in `~/.config/bananahub/templates/` and take precedence over built-ins on ID conflict.

### Creating Your Own Template

Run `/bananahub create-template` for a guided wizard: first choose `prompt` or `workflow`, then gather intent, draft the body, generate samples when useful, and assemble the final `template.md`.

Prompt templates use `{{variable|default value}}` slots with a variables table and tips section. Workflow templates use sections such as `Goal`, `Inputs`, `Steps`, and `Prompt Blocks`. Full spec in `references/template-format-spec.md`.

Publishing checklist:

- Name each sample with the generating model shorthand, for example `sample-3-pro-01.png`
- Keep `template.md` sample metadata exact: `file`, `model`, `prompt`, `aspect`
- Add `README.md` sections for `Verified Models`, `Supported Models`, and `Sample Outputs`
- In `Sample Outputs`, map every sample file to the model and exact prompt or variant it validates

## How Prompt Optimization Works

```
User input (non-English or mixed-language)
  │
  ├─ Phase 0: Constraint Extraction
  │   └─ exact text / keep / avoid / platform / invariants
  │
  ├─ Phase 1: Base Optimization (silent)
  │   ├─ Format correction (fix keyword dumps, SD syntax, etc.)
  │   ├─ Smart translation (descriptive text → English, in-image text → preserved)
  │   └─ Structuring + conservative guardrails
  │
  ├─ Phase 2: Intent Recognition
  │   └─ Match to profile: photo / illustration / diagram / text-heavy / minimal / sticker / 3d / product / concept-art / general
  │
  └─ Phase 3: Enhancement (if profile matched)
      └─ Load profile-specific rules → fill only justified dimensions → confirm high-impact additions with user
```

## Available Models

| Model | Alias | Best For |
|---|---|---|
| `gemini-3-pro-image-preview` | Gemini 3 Pro Image (default) | High quality, complex scenes, text rendering |
| `gemini-3.1-flash-image-preview` | Gemini 3.1 Flash Image | Better quality-speed balance, stronger iteration and text rendering than older Flash models |
| `gemini-2.5-flash-image` | Gemini 2.5 Flash Image | Fast generation, rapid iteration |

`gemini-2.0-flash-preview-image-generation` remains as a legacy fallback for older setups, but it is no longer the primary Flash recommendation.

## Project Structure

```text
bananahub-skill/
├── SKILL.md                          # Skill definition (Claude Code entry point)
├── scripts/
│   ├── bananahub.py                  # Primary image generation entrypoint
└── references/
    ├── prompt-guide.md               # Prompt optimization rules
    ├── official-sources.md           # Authoritative references & example library
    └── profiles/                     # Intent-specific enhancement profiles
        ├── photo.md
        ├── illustration.md
        ├── diagram.md
        ├── text-heavy.md
        ├── minimal.md
        ├── sticker.md
        ├── 3d.md
        ├── product.md
        ├── concept-art.md
        └── general.md
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with skill support
- Python 3.8+
- Gemini API key from Google AI Studio or a Gemini-compatible relay provider
- Billing/quota depends on Google's current policy, your model choice, and your account/region

## Contributing

Code and docs contributions to this repo are accepted under MIT and should be signed off with:

```bash
git commit -s -m "feat: your change"
```

If you contribute built-in templates under `references/templates/`, keep the frontmatter `license` field explicit, keep the samples redistributable, and treat template content as CC BY 4.0 unless the template directory states otherwise.

## License

- Code, scripts, and general repo docs: MIT
- Built-in templates and bundled sample assets under `references/templates/`: CC BY 4.0 unless a template directory states otherwise
