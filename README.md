# Nano Banana 🍌

A [Claude Code Skill](https://docs.anthropic.com/en/docs/claude-code/skills) that turns Chinese image descriptions into optimized English prompts and generates images via the Gemini API.

## What It Does

1. **Smart prompt optimization** — Translates Chinese descriptions into high-quality English prompts, fixing common issues (keyword dumps, SD/MJ syntax, negative phrasing, etc.)
2. **Intent-aware enhancement** — Automatically detects image intent (photo, illustration, diagram, text-heavy, minimal, sticker, 3D, product, concept-art) and applies domain-specific prompt enhancements
3. **In-image text preservation** — Keeps Chinese text meant to appear in the image (e.g. `写着"生日快乐"的蛋糕` → `a cake with the text "生日快乐"`)
4. **Multiple generation modes** — Default (interactive), Direct (no confirmations), and Raw (translate-only)

## Installation

```bash
claude skill install /path/to/nanobanana
# or from GitHub
claude skill install https://github.com/zkywalker/nanobanana
```

## Setup

After installation, run the init command to configure your environment:

```
/nanobanana init
```

This will:
- Install Python dependencies (`google-genai`, `pillow`)
- Guide you through setting up your Gemini API key in `~/.gemini/.env`
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
| `--direct` | Skip all confirmations, trust optimization fully |
| `--raw` | Translate only, no optimization |
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

## How Prompt Optimization Works

```
User input (Chinese)
  │
  ├─ Phase 1: Base Optimization (silent)
  │   ├─ Format correction (fix keyword dumps, SD syntax, etc.)
  │   ├─ Smart translation (descriptive → English, in-image text → preserved)
  │   └─ Structuring (subject first, add trigger prefix)
  │
  ├─ Phase 2: Intent Recognition
  │   └─ Match to profile: photo / illustration / diagram / text-heavy / minimal / sticker / 3d / product / concept-art / general
  │
  └─ Phase 3: Enhancement (if profile matched)
      └─ Load profile-specific rules → fill missing dimensions → confirm with user
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
