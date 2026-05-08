# Capability Registry

This registry defines provider/model capabilities used by the skill, runtime, templates, and catalog. Treat capabilities as routing constraints, not marketing labels.

## Core Capabilities

| Capability | Meaning | Routing Impact |
|---|---|---|
| `text_to_image` | Generate an image from text only | Required for `generate` |
| `image_edit` | Edit an existing image with text instructions | Required for `edit` |
| `mask_edit` | Edit only masked regions | Prefer GPT Image/OpenAI-native routes when requested |
| `multi_reference` | Accept multiple input/reference images | Validate max image count before execution |
| `transparent_background` | Generate transparent or alpha-aware output | Route to providers with explicit support |
| `custom_size` | Accept exact pixel dimensions | Use provider-specific size validation |
| `native_quality` | Accept native quality presets | Map only when the provider supports them |
| `output_format` | Choose output encoding such as PNG/JPEG/WebP | Route option through provider adapter |
| `grounding` | Use current external data during image planning | Gemini-specific unless another provider exposes it |

## Capability Layers

Not every BananaHub capability belongs at the same layer. Keep cross-model behavior in the skill layer, and keep provider/model-specific behavior behind registries and adapters.

| Layer | Cross-Model? | Belongs Here | Examples |
|---|---|---|---|
| Skill workflow | Yes | Behavior the agent can perform before any provider call | prompt optimization, translation policy, `--direct` / `--raw`, prompt archiving, host-native delegation, prompt-only advisor fallback |
| Template routing | Partly | Template selection and activation are common, but compatibility is provider/model-scoped | local/installed template lookup, variable filling, workflow state, provider compatibility matrix |
| Provider family | No | Features exposed by one provider family or transport | Gemini aspect ratio and image-size presets, OpenAI `size` / `quality` / `background`, chat image URL extraction |
| Model profile | No | Per-model aliases, default model, fallback chain, tested quality, and prompt variants | `gemini-3-pro-image-preview`, `gpt-image-2`, template `prompt_variant` and sample provenance |
| Endpoint/runtime | No | Config, auth, base URL normalization, healthcheck, and vendor-specific transport constraints | `google-ai-studio`, `openai`, `openai-compatible`, `chatgpt-compatible` |

### Cross-Model Rule

Treat these as cross-model skill-layer capabilities because they can run before any image API is available: prompt optimization, translation policy, conservative enhancement, prompt archiving, mode detection, template discovery, template activation, host-native delegation, and prompt-only advisory output.

Treat these as **not** cross-model unless a registry/provider adapter explicitly says otherwise: image edit, mask edit, multiple reference images, transparent background, exact size control, native quality presets, output format/compression, model fallback, and generated-image fidelity.

If a capability changes request payload shape, file validation, cost, policy behavior, or output parsing, it belongs below the skill layer and must be routed through provider/model metadata instead of being assumed globally.

## Provider Capability Profiles

### `gemini-image`

- Supports text-to-image and image+text editing through Gemini image models.
- Uses `aspect_ratio` and native image-size presets such as `1K`, `2K`, and `4K` where supported.
- Supports multi-reference workflows; Gemini 3 image flows use up to 14 total input images.
- Prompting favors natural descriptive English, explicit quoted in-image text, and concise task constraints.
- Model aliases such as `nano-banana`, `nano-banana-pro`, and `nano-banana-2` resolve through `model-registry.json`.

### `gpt-image`

- Supports text-to-image through OpenAI Images API.
- Supports image editing, multi-image references, and mask editing through OpenAI-native image endpoints or Responses API image generation tools.
- Uses OpenAI-native options such as `size`, `n`, `quality`, `background`, `output_format`, `output_compression`, and `moderation` when supported by the selected model.
- Prompting should be stricter about layout, exact text, edit deltas, and "keep everything else unchanged" instructions.
- Do not inherit Gemini-specific limits such as 14 reference images or `1K/2K/4K` size presets unless the selected OpenAI model/provider explicitly supports an equivalent.

### `unknown-openai-compatible`

- Represents third-party OpenAI-style endpoints with unknown image capabilities.
- The runtime can attempt standard Images API generation, editing, multi-image references, and mask fields.
- Do not assume model-specific quality, pricing, size constraints, or advanced options beyond what the gateway actually accepts.
- Require explicit configured capabilities or a successful provider call before advertising advanced features as verified.

## Selection Policy

Provider/model selection follows this priority:

1. Explicit command flags: `--provider`, `--profile`, `--model`.
2. Active workflow/template state from the current conversation.
3. Template compatibility matrix and best-tested model.
4. User default profile from `~/.config/bananahub/config.json`.
5. Capability requirement inferred from the task, for example mask editing or transparent output.
6. Built-in default provider/model.

Do not cross provider boundaries during fallback unless the user explicitly enables cross-provider fallback. Cross-provider fallback can change visual style, cost, policy behavior, and template validity.

### `chat-image`

- Represents chat/completions-style endpoints that can return images inside assistant messages.
- BananaHub asks the model to include a markdown image URL or `data:image/...;base64` URL in the response, then extracts and saves the image.
- Do not assume OpenAI Images API options, mask editing, exact size control, or edit support.
- Treat output parsing as best-effort because each vendor may format image replies differently.
- If a chat endpoint returns a protected `chatgpt.com/backend-api/estuary/content` URL, BananaHub may not be able to download it without browser/session credentials. In that case runtime returns `status: partial` and saves reference metadata.

## Adapter Extension Contract

Provider-specific runtime code lives under `scripts/providers/`. New providers should expose small functions with the same shape as existing adapters:

- `try_generate(...) -> (image_bytes, warnings, error)` for byte-producing providers.
- `try_edit(...) -> (image_bytes, warnings, error)` when image edit is supported.
- `list_models(...)` only when the provider exposes model discovery.
- Adapter functions should not print, exit, or read CLI args directly; `bananahub.py` owns CLI behavior and result formatting.
- Provider adapters may accept injected normalizers/resolvers from `bananahub.py` to avoid import cycles.
- Provider constants, aliases, transport defaults, endpoint normalization, and config-key mappings live in `scripts/runtime_config.py`. Update that module first when adding a provider.
- Config loading, profile merging, validation, command-scoped provider overrides, and display serialization live in `scripts/config_store.py`. Update it when a provider needs new config fields or validation rules.
