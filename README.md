# Nano Banana 🍌

[简体中文说明](./README.zh-CN.md)

A [Claude Code Skill](https://docs.anthropic.com/en/docs/claude-code/skills) that turns Chinese image descriptions into optimized English prompts and generates images via the Gemini API.

## Product Summary

Nano Banana is not just a prompt optimizer. It is an agent-native image workflow for Gemini inside Claude Code:

- **Agent-native runtime** — optimization, generation, editing, template use, and iteration happen in the same conversation
- **Progressive disclosure guidance** — the skill stays quiet on low-risk cleanup, asks only when ambiguity would materially change the result, and suggests templates only when there is a strong match
- **Installable template ecosystem** — built-ins cover common jobs, while BananaHub lets users discover and install extra prompt modules without bloating the base skill

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
| `/nanobanana init` | Check/setup environment |
| `/nanobanana help` | Show usage instructions |

### Flags

| Flag | Description |
|---|---|
| `--direct` | Skill-layer mode: skip confirmations, but still keep enhancement conservative |
| `--raw` | Skill-layer mode: translate only, no optimization |
| `--model <id>` | Specify model (`gemini-3-pro-image-preview` or `gemini-2.0-flash-preview-image-generation`) |
| `--aspect <ratio>` | Aspect ratio (e.g. `16:9`, `1:1`, `9:16`) |
| `--size <WxH>` | Output dimensions (e.g. `1024x1024`) |
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

# Specify aspect ratio and model
/nanobanana 山水画风格的桂林风景 --aspect 16:9 --model gemini-2.0-flash-preview-image-generation

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

# Edit with custom output path
/nanobanana edit 添加一顶圣诞帽 --input avatar.png --output avatar_xmas.png
```

## Templates

Built-in templates are curated prompt modules with variable slots. Use them directly, override only the pieces you care about, or install more from BananaHub when a repeatable job deserves its own module.

### Template Commands

| Command | Description |
|---|---|
| `/nanobanana templates` | List all available templates |
| `/nanobanana templates <name>` | Show template details, variables, and tips |
| `/nanobanana use <name>` | Generate using template defaults |
| `/nanobanana use <name> <描述>` | Generate with custom variable overrides |
| `/nanobanana create-template` | AI-guided template creation wizard |

### Examples

```bash
# List all templates
/nanobanana templates

# Preview a template
/nanobanana templates cyberpunk-city

# Generate with defaults
/nanobanana use cyberpunk-city

# Override variables with a description
/nanobanana use cyberpunk-city 东京新宿街头，紫色和金色霓虹

# Use with flags
/nanobanana use cyberpunk-city 上海外滩未来版 --aspect 9:16
```

### Built-in Templates

| ID | Title | Profile |
|---|---|---|
| `cyberpunk-city` | 赛博朋克城市夜景 | photo |
| `cute-sticker` | Q版贴纸表情包 | sticker |
| `product-white-bg` | 电商白底产品图 | product |
| `info-diagram` | 信息图/流程图 | diagram |
| `minimal-wallpaper` | 极简手机壁纸 | minimal |

### Installing More Templates (BananaHub)

```bash
# Search the community hub
npx bananahub search <keyword>

# Install a template from GitHub
npx bananahub add <username>/<repo>
```

User-installed templates are stored in `~/.config/nanobanana/templates/` and take precedence over built-ins on ID conflict.

### Creating Your Own Template

Run `/nanobanana create-template` for a guided 4-phase wizard: intent gathering → prompt drafting → sample generation → assembly. The wizard generates a `template.md` ready to publish on GitHub or submit to BananaHub.

Template format: `{{variable|default value}}` slots in the prompt, with a variables table and tips section. Full spec in `references/template-format-spec.md`.

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
| `gemini-2.0-flash-preview-image-generation` | Nano Banana Flash | Fast generation, rapid iteration |

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
