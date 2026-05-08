# OpenAI GPT Image Provider Guide

Use this guide only after the core optimization pipeline has selected OpenAI GPT Image or a GPT Image-specific capability.

## Model Family

GPT Image models are OpenAI-native image models. Use provider id `openai` for official OpenAI APIs. `openai-compatible` can attempt the same Images API paths, but gateway-specific support must be verified.

Canonical model ids and aliases are resolved through `references/model-registry.json`.

## Prompt Preferences

- Keep the same conservative core optimization rules: subject first, natural English, exact in-image text in quotes, and no SD/MJ weight syntax.
- Be more explicit about layout, typography, spacing, and reading order for text-heavy outputs.
- For edits, write the allowed delta and preservation constraints directly: change only the requested element and keep composition, identity, text, colors, and background unchanged unless the user says otherwise.
- For mask edits, describe the intended content inside the masked region and avoid asking the model to reinterpret the whole image.
- Use short, exact text strings for in-image text; ask for confirmation when the requested copy is long or unstable.

## Runtime Options

- Use OpenAI-native `size`, `n`, `quality`, `background`, `output_format`, `output_compression`, and `moderation` only when the selected model supports them. BananaHub exposes these as `--openai-size`, `--n`, `--quality`, `--background`, `--output-format`, `--output-compression`, and `--moderation`.
- Do not map Gemini `aspect_ratio` or `1K/2K/4K` presets directly to GPT Image. Convert intent through the OpenAI provider adapter.
- OpenAI-native edit and mask edit should be routed to the OpenAI provider adapter, not the legacy Gemini `openai-compatible` path.
- BananaHub exposes multi-image editing with `edit --input <source.png> --ref <reference...>` and mask editing through `edit --mask <mask.png>` for the OpenAI-native provider.
- Validate image/mask file requirements in the provider adapter before calling the API.

## Template Guidance

Templates with materially different GPT Image behavior should define `prompt_variant: gpt-image` and provide GPT Image-specific samples. If a template is untested on GPT Image, mark quality as `untested` or omit the OpenAI model entry rather than implying support.
