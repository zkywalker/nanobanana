# Nano Banana 🍌

[简体中文说明](./README.zh-CN.md)

A [Claude Code Skill](https://docs.anthropic.com/en/docs/claude-code/skills) that turns Chinese image descriptions into optimized English prompts and generates images via the Gemini API.

## Product Summary

Nano Banana is not just a prompt optimizer. It is an agent-native image workflow for Gemini inside Claude Code:

- **Agent-native runtime** — optimization, generation, editing, template use, and iteration happen in the same conversation
- **Progressive disclosure guidance** — the skill stays quiet on low-risk cleanup, asks only when ambiguity would materially change the result, and suggests templates only when there is a strong match
- **Installable template ecosystem** — built-ins cover common jobs, while BananaHub lets users discover and install extra prompt or workflow modules without bloating the base skill

## What It Does

1. **Smart prompt optimization** — Translates Chinese descriptions into high-quality English prompts, fixing common issues (keyword dumps, SD/MJ syntax, negative phrasing, etc.)
2. **Conservative intent-aware enhancement** — Detects image intent (photo, illustration, diagram, text-heavy, minimal, sticker, 3D, product, concept-art) and applies domain-specific enhancements without inventing unnecessary style decisions
3. **In-image text preservation** — Keeps Chinese text meant to appear in the image (e.g. `写着"生日快乐"的蛋糕` → `a cake with the text "生日快乐"`)
4. **Constraint-first workflow** — Extracts exact text, keep/avoid constraints, target use, and edit invariants before generating
5. **Multiple generation modes** — Default (interactive), Direct (no confirmations), and Raw (translate-only)
6. **Template-driven reuse and distribution** — Uses built-in templates, supports AI-guided template creation, and connects to BananaHub for searchable installation

## Design Principles

- **Ask instead of guess** when multiple plausible directions would materially change the result
- **Do not add high-impact details lightly**: background, palette, lighting mood, lens language, texture, extra props
- **Treat text and structure as locked content** for posters, logos, diagrams, and information graphics
- **Use English for the final prompt by default**; preserve original language only for in-image text and locked names/labels
- **For edits, preserve invariants first** and change only the requested delta
- **Iterate one major variable at a time** for follow-up revisions

## Installation

```bash
claude skill install /path/to/nanobanana
# or from GitHub
claude skill install https://github.com/nano-banana-hub/nanobanana
```

## Setup

After installation, run the init command to configure your environment:

```
/nanobanana init
```

This will:
- Install Python dependencies (`google-genai`, `pillow`)
- Guide you through setting up your Gemini API key in one of the supported config sources
- Test API connectivity

**Get a Gemini API key**: https://aistudio.google.com/apikey (free tier available)

## Usage

```
/nanobanana 一只橘猫趴在键盘上打盹
```

### Commands

| Command | Description |
|---|---|
| `/nanobanana <中文描述>` | Optimize prompt + generate image |
| `/nanobanana edit <描述> --input <图片>` | Edit an existing image with a text prompt |
| `/nanobanana optimize <描述>` | Optimize prompt only (no generation) |
| `/nanobanana generate <English prompt>` | Generate with an English prompt directly |
| `/nanobanana models` | List available models |
| `/nanobanana discover <need>` | Search BananaHub for matching templates and suggest install candidates |
| `/nanobanana discover trending` | Show current trending BananaHub templates |
| `/nanobanana init` | Check/setup environment |
| `/nanobanana help` | Show usage instructions |

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
/nanobanana 赛博朋克风格的东京街头夜景

# Direct mode — no confirmations
/nanobanana 水彩风格的猫咪 --direct

# Raw mode — translate only, no optimization
/nanobanana 一个简单的红色圆圈 --raw

# Specify aspect ratio, model, and native image size
/nanobanana 山水画风格的桂林风景 --aspect 16:9 --model gemini-2.5-flash-image --image-size 2K

# Sticker / emoji
/nanobanana 画一个开心的柴犬表情包

# 3D render
/nanobanana 等距视角的咖啡店室内设计

# Product photography
/nanobanana 白底蓝牙耳机产品图

# Concept art
/nanobanana 赛博朋克风格的女性角色设计

# Edit an existing image
/nanobanana edit 把背景换成海滩 --input photo.png

# Edit with native 2K output, then resize for delivery
/nanobanana edit 添加一顶圣诞帽 --input avatar.png --image-size 2K --resize 1024x1024 --output avatar_xmas.png
```

## Templates

Built-in templates are reusable agent modules. Some are `prompt` templates that assemble one reusable prompt. Others are `workflow` templates that load a guided multi-step playbook. Use them directly, override only the pieces you care about, or install more from BananaHub when a repeatable job deserves its own module.

### Template Commands

| Command | Description |
|---|---|
| `/nanobanana templates` | List all available templates |
| `/nanobanana templates <name>` | Show template details based on its type |
| `/nanobanana use <name>` | Activate a prompt template or start a workflow template |
| `/nanobanana use <name> <描述>` | Activate with custom variable overrides or workflow context |
| `/nanobanana discover <need>` | Search BananaHub and recommend remote templates |
| `/nanobanana create-template` | AI-guided prompt/workflow template creation wizard |

### Examples

```bash
# List all templates
/nanobanana templates

# Preview a template
/nanobanana templates cyberpunk-city

# Generate with prompt-template defaults
/nanobanana use cyberpunk-city

# Override prompt-template variables with a description
/nanobanana use cyberpunk-city 东京新宿街头，紫色和金色霓虹

# Start a workflow template
/nanobanana use consistent-character-storyboard

# Ask Nano Banana to search BananaHub for a matching workflow
/nanobanana discover logo 品牌标识

# Use with flags
/nanobanana use cyberpunk-city 上海外滩未来版 --aspect 9:16
```

### Workflow Spotlight

`consistent-character-storyboard` is the built-in example of a multi-step workflow template. It is meant for character-consistency storyboard exploration rather than one-shot final art.

Typical flow:

```bash
# Step 1: create or approve one master reference
/nanobanana 一个可爱的暹罗猫IP，奶油色毛发，深棕色重点色，蓝眼睛，戴青绿色小围巾和金色铃铛

# Step 2: start the workflow template
/nanobanana use consistent-character-storyboard
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
| `asset-style-consistency-pack` | workflow | 本地素材风格统一工作流 | general |

### Installing More Templates (BananaHub)

Use `/nanobanana discover <need>` when you want the skill to search BananaHub for you, rank a few candidates, and continue directly into installation and activation.

```bash
# Ask the skill to search BananaHub
/nanobanana discover repository explainer diagram

# Search the hub directly from the CLI
npx bananahub search <keyword>

# Install a template from GitHub when the install target is already known
npx bananahub add <username>/<repo>
```

User-installed templates are stored in `~/.config/nanobanana/templates/` and take precedence over built-ins on ID conflict.

### Creating Your Own Template

Run `/nanobanana create-template` for a guided wizard: first choose `prompt` or `workflow`, then gather intent, draft the body, generate samples when useful, and assemble the final `template.md`.

Prompt templates use `{{variable|default value}}` slots with a variables table and tips section. Workflow templates use sections such as `Goal`, `Inputs`, `Steps`, and `Prompt Blocks`. Full spec in `references/template-format-spec.md`.

Publishing checklist:

- Name each sample with the generating model shorthand, for example `sample-3-pro-01.png`
- Keep `template.md` sample metadata exact: `file`, `model`, `prompt`, `aspect`
- Add `README.md` sections for `Verified Models`, `Supported Models`, and `Sample Outputs`
- In `Sample Outputs`, map every sample file to the model and exact prompt or variant it validates

## How Prompt Optimization Works

```
User input (Chinese)
  │
  ├─ Phase 0: Constraint Extraction
  │   └─ exact text / keep / avoid / platform / invariants
  │
  ├─ Phase 1: Base Optimization (silent)
  │   ├─ Format correction (fix keyword dumps, SD syntax, etc.)
  │   ├─ Smart translation (descriptive → English, in-image text → preserved)
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
| `gemini-3-pro-image-preview` | Nano Banana Pro (default) | High quality, complex scenes, text rendering |
| `gemini-3.1-flash-image-preview` | Nano Banana 2 | Better quality-speed balance, stronger iteration and text rendering than older Flash models |
| `gemini-2.5-flash-image` | Nano Banana | Fast generation, rapid iteration |

`gemini-2.0-flash-preview-image-generation` remains as a legacy fallback for older setups, but it is no longer the primary Flash recommendation.

## Project Structure

```
nanobanana/
├── SKILL.md                          # Skill definition (Claude Code entry point)
├── scripts/
│   └── nanobanana.py                 # Image generation CLI tool
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
- Gemini API key ([get one free](https://aistudio.google.com/apikey))

## License

MIT
