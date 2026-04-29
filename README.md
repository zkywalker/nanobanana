# BananaHub Skill 🍌

[简体中文说明](./README.zh-CN.md)

BananaHub is an agent-native image workflow skill. Describe what you want in Chinese, English, or mixed language; BananaHub cleans up the prompt, detects the available runtime, routes the task to the right image path, and keeps generation, editing, templates, and reusable prompts under one `/bananahub` command.

It is not just a prompt helper. BananaHub acts as a workflow layer between agents and image providers: Gemini / Nano Banana, OpenAI GPT Image, compatible gateways, and host-native image tools.

## Why BananaHub

- **Works in more environments**: direct provider calls when keys are configured, host-tool delegation when the client already has image generation, prompt-only output when no image runtime is available.
- **Less rework**: locks text, layout, preserved elements, and edit boundaries before generation.
- **Multi-model without guesswork**: prompt cleanup and archiving are cross-model; mask edits, native sizes, reference limits, quality presets, and output formats stay provider/model-scoped.
- **Reusable by default**: archive final prompts for handoff, QA, reruns, and template authoring.
- **Template-ready**: use built-ins, install more from BananaHub, or create repeatable prompt/workflow modules.

## Quick Start

```bash
# Open Agent Skills / skills.sh
npx skills add https://github.com/bananahub-ai/bananahub-skill --skill bananahub

# Or install directly in Claude Code
claude skill install https://github.com/bananahub-ai/bananahub-skill

/bananahub init
/bananahub 一只橘猫趴在键盘上打盹
```

Check the current execution path:

```bash
python3 scripts/bananahub.py check-mode --pretty
```

## Runtime Modes

| Mode | When It Applies | What BananaHub Does |
|---|---|---|
| `provider-backed` | A supported provider and key are configured | Optimizes the prompt, calls the provider, and saves outputs |
| `host-native` | Local provider config is incomplete, but the host agent has an image tool | Optimizes/archives the prompt, then delegates image generation to the host |
| `prompt-only` | No provider and no host image tool are available | Returns a reusable prompt; never pretends an image was generated |

For CLI checks, use `BANANAHUB_HOST_IMAGEGEN=1` or `check-mode --host-imagegen` to mark host-native image generation as available.

## Best Fit

- **Everyday visual work**: product clean shots, background replacement, article one-pagers, infographics, and repo explainers.
- **Knowledge visuals**: turn processes, long-form content, or codebase context into readable one-image summaries.
- **Provider-aware teams**: use the same template IDs across Gemini / Nano Banana and OpenAI GPT Image without hiding model-specific limits.
- **Reusable workflows**: archive prompts and install richer templates from BananaHub instead of bloating the skill package.

## Commands

| Command | Use |
|---|---|
| `/bananahub <description>` | Optimize the prompt and generate an image |
| `/bananahub edit <description> --input <image>` | Edit an existing image |
| `/bananahub optimize <description>` | Optimize only, no generation |
| `/bananahub generate <English prompt>` | Generate directly from an English prompt |
| `/bananahub models` | List available models |
| `/bananahub check-mode` | Inspect runtime mode and capability layers |
| `/bananahub templates` | List built-in and installed templates |
| `/bananahub use <template-id>` | Use a prompt template or start a workflow template |
| `/bananahub discover <need>` | Search BananaHub for matching templates |
| `/bananahub init` | Check and initialize the environment |

## Common Flags

| Flag | Meaning |
|---|---|
| `--direct` | Fewer confirmations; still conservative about creative additions |
| `--raw` | Translate/clean only, no extra enhancement |
| `--model <id>` | Select a model, e.g. `gemini-3-pro-image-preview`, `gpt-image-2` |
| `--provider <id>` | Override provider for one run, e.g. `openai`, `google-ai-studio` |
| `--aspect <ratio>` | Aspect ratio, e.g. `16:9`, `1:1`, `9:16` |
| `--image-size <preset>` | Gemini native size preset: `1K`, `2K`, `4K` |
| `--openai-size <value>` | OpenAI Images API native size option |
| `--resize <WxH>` | Resize after generation/editing |
| `--output <path>` | Image output path |
| `--save-prompt` | Archive the final prompt under `bananahub-prompts/` |
| `--prompt-output <path>` | Save the final prompt to a file or directory |
| `--input <path>` | Source image for edit commands |
| `--ref <path...>` | Reference images for edit commands |
| `--mask <path>` | OpenAI-native mask edit |

Set `BANANAHUB_SAVE_PROMPTS=1` to archive final prompts by default for generate/edit runs.

## Prompt Archive

Prompt archive is useful for QA, handoff, reruns, provider switching, and template design.

```bash
python3 scripts/bananahub.py generate \
  "A clean product photo of a blue wireless earbud case" \
  --save-prompt

python3 scripts/bananahub.py generate \
  "A launch poster for BananaHub" \
  --prompt-output docs/prompts/launch-poster.md
```

The archive file stores command metadata, provider, model, timestamp, and the final prompt. It is written before the provider call, so a failed API request still leaves a reusable prompt behind.

## Provider Paths

BananaHub supports several provider routes. Advanced capabilities are not assumed globally; use `check-mode` and the capability registry to verify what is available.

| Provider | Best For | Generate | Edit | Mask | Notes |
|---|---|---:|---:|---:|---|
| `google-ai-studio` | Default path for individuals and teams | ✅ | ✅ | — | Gemini / Nano Banana route |
| `gemini-compatible` | Gemini-style relays or proxies | ✅ | ✅ | — | Depends on the relay |
| `vertex-ai` | Enterprise GCP / Vertex AI | ✅ | ✅ | — | ADC or API key auth |
| `openai` | Official OpenAI GPT Image APIs | ✅ | ✅ | ✅ | GPT Image native route |
| `openai-compatible` | OpenAI-style gateways | ✅ | Gateway-dependent | Gateway-dependent | No advanced capability is assumed |
| `chatgpt-compatible` | Chat/completions endpoints that return images | ✅ | — | — | Best-effort URL/base64 extraction |

Setup examples:

```bash
# Inspect active config and capabilities
python3 scripts/bananahub.py config show
python3 scripts/bananahub.py check-mode --pretty

# Google AI Studio / Gemini Developer API
python3 scripts/bananahub.py config set --provider google-ai-studio --api-key <your_api_key>

# Gemini-compatible relay
python3 scripts/bananahub.py config set --provider gemini-compatible --base-url https://your-gemini-endpoint --api-key <your_key>

# OpenAI GPT Image
python3 scripts/bananahub.py config set --provider openai --api-key <your_openai_key> --model gpt-image-2

# OpenAI-compatible gateway
python3 scripts/bananahub.py config set --provider openai-compatible --base-url https://your-openai-compatible-endpoint --api-key <your_key>

# Chat/completions-compatible image endpoint
python3 scripts/bananahub.py config set --provider chatgpt-compatible --base-url https://your-chat-endpoint --api-key <your_key> --model gpt-5.4

# Vertex AI
python3 scripts/bananahub.py config set --provider vertex-ai --auth-mode adc --project <gcp-project> --location global
```

Config priority: `--config <file>` → environment variables → `~/.config/bananahub/config.json`.

## How Prompt Optimization Works

```text
User input
  │
  ├─ Extract constraints: exact text / keep / avoid / platform / edit invariants
  ├─ Clean up: keyword dumps, SD/MJ syntax, negative phrasing, buried subjects
  ├─ Translate smartly: descriptive content → English; in-image text and proper names stay locked
  ├─ Detect intent: photo / product / diagram / sticker / text-heavy / 3d / concept-art ...
  └─ Enhance conservatively: add only useful detail; confirm high-impact creative choices
```

This layer is cross-model. Provider-dependent features such as mask edit, exact size, transparent background, quality presets, and reference-image limits are routed through provider/model metadata.

## Templates

Templates come in two shapes:

- **Prompt templates** assemble one reusable prompt for stable jobs such as product clean shots, infographic cards, or background replacement edits.
- **Workflow templates** guide multi-step jobs such as article one-page summaries or repository explainer diagrams.

```bash
/bananahub templates
/bananahub templates article-one-page-summary
/bananahub use info-diagram "PR review flow: Change, Review, Test, Fix, Merge"
/bananahub use background-replace-edit --input product.png
/bananahub discover logo system
/bananahub create-template
```

Built-ins are a lean starter pack: `product-white-bg`, `info-diagram`, `article-one-page-summary`, `repo-explainer-diagram`, and `background-replace-edit`. They are practical, low-maintenance, sample-free, and support both Gemini/Nano Banana and OpenAI GPT Image through provider-specific prompt variants.

Install richer official templates from `bananahub-ai/templates` through BananaHub discovery when you need style packs, logo systems, character workflows, campaign visuals, or heavier sample galleries. Community templates remain available through the broader catalog. User-installed templates live in `~/.config/bananahub/templates/` and take precedence over built-ins with the same ID.

## References

- Prompt rules: `references/prompt-guide.md`
- Capability layers: `references/capability-registry.md`
- Model registry: `references/model-registry.json`
- Template spec: `references/template-format-spec.md`
- Official sources: `references/official-sources.md`

## Requirements

- Claude Code / Open Agent Skills runtime with skill support
- Python 3.8+
- Optional: `google-genai`, `pillow`
- Optional: Gemini, OpenAI, or compatible gateway API key

## Contributing

Code and docs contributions are accepted under MIT. Built-in starter templates under `references/templates/` should stay lightweight and explicitly licensed; heavier sample galleries belong in official or community template repositories.

## License

- Code, scripts, and general repo docs: MIT
- Built-in starter templates under `references/templates/`: CC BY 4.0 unless a template directory states otherwise
