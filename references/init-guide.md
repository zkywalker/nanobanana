# Initialization Flow

When the user runs `init`, make BananaHub usable with the least possible back-and-forth. Agents should persist image API connection details with non-interactive `config quickset` profile writes.

## Agent Rules

1. Do not assume the agent can run interactive TTY prompts.
2. Start with machine-readable diagnosis:
   ```bash
   python3 {baseDir}/scripts/bananahub.py config doctor --json
   ```
3. If provider fields are missing, ask only for the missing provider-required values.
4. Direct API-key entry is allowed when the user chooses it or already pasted a key. Write it with `config quickset --api-key-stdin` and do not echo it back.
5. If the user does not want secrets in chat, provide the matching `config quickset` command with placeholders for their local terminal.
6. Use the interactive wizard only as a human-terminal fallback:
   ```bash
   python3 {baseDir}/scripts/bananahub.py init --wizard
   ```
7. If dependencies are missing and the user allows package installation, run `dependency_install_command` from `config doctor --json`; do not add `--break-system-packages` automatically.
8. Do not run a paid image-generation test unless the user explicitly agrees. Model-list healthchecks are okay; generation smoke tests require consent.
9. Default to GPT Image 2 through `openai-compatible` unless the user explicitly chooses another image channel or an existing config already resolves cleanly.
10. Do not ask the user to interpret `resolved_from`, provider aliases, or ignored env vars. Use `effective_config`, `missing_fields`, and `ignored_config_sources` yourself and only surface the next action.
11. Treat the persisted default profile as the user's durable choice. Environment variables fill missing fields by default; they override profile fields only when `BANANAHUB_ENV_OVERRIDE=1` is set.

## Provider Selection

Ask one human question first: “Which image channel do you already have?”

- **OpenAI-compatible gateway** — Cherry Studio / Bigfish / other OpenAI-style image gateway. Default profile `gpt`, default model `gpt-image-2`.
- **OpenAI official** — official GPT Image API. Default profile `gpt`, default model `gpt-image-2`.
- **Google AI Studio** — Gemini / Nano Banana route. Default profile `nano`, default model `gemini-3-pro-image-preview`.
- **Gemini-compatible gateway** — Gemini-style relay/proxy. Default profile `nano`.
- **Vertex AI** — enterprise GCP route. Default profile `vertex`, usually `auth_mode=adc`.
- **ChatGPT-compatible** — chat/completions endpoint that returns image URLs/base64 in assistant messages. Default profile `chat`.

## One-Line Setup Commands

OpenAI-compatible gateway:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider openai-compatible --profile gpt --default-profile \
  --base-url "<openai-compatible base url>" --api-key "<api key>" --model gpt-image-2
```

Agent direct-entry variant:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider openai-compatible --profile gpt --default-profile \
  --base-url "<openai-compatible base url>" --api-key-stdin --model gpt-image-2
```

OpenAI official:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider openai --profile gpt --default-profile \
  --api-key "<openai api key>" --model gpt-image-2
```

Agent direct-entry variant:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider openai --profile gpt --default-profile \
  --api-key-stdin --model gpt-image-2
```

Google AI Studio:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider google-ai-studio --profile nano --default-profile \
  --api-key "<google api key>" --model gemini-3-pro-image-preview
```

Agent direct-entry variant:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider google-ai-studio --profile nano --default-profile \
  --api-key-stdin --model gemini-3-pro-image-preview
```

Gemini-compatible gateway:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider gemini-compatible --profile nano --default-profile \
  --base-url "<gemini-compatible base url>" --api-key "<api key>" --model gemini-3-pro-image-preview
```

Agent direct-entry variant:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider gemini-compatible --profile nano --default-profile \
  --base-url "<gemini-compatible base url>" --api-key-stdin --model gemini-3-pro-image-preview
```

Vertex AI ADC:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider vertex-ai --profile vertex --default-profile \
  --auth-mode adc --project "<gcp-project>" --location global
```

ChatGPT-compatible endpoint:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider chatgpt-compatible --profile chat --default-profile \
  --base-url "<chat endpoint>" --api-key "<api key>" --model gpt-5.4
```

Agent direct-entry variant:
```bash
python3 {baseDir}/scripts/bananahub.py config quickset --provider chatgpt-compatible --profile chat --default-profile \
  --base-url "<chat endpoint>" --api-key-stdin --model gpt-5.4
```

## Profile Config Contract

`config quickset` writes `~/.config/bananahub/config.json`. Prefer named profiles so users can switch API keys, endpoints, and models later without rebuilding setup.

Default precedence is:

1. `--config <file>` for an explicit one-off config
2. selected profile from `~/.config/bananahub/config.json`
3. environment variables as fallback values for fields not present in the selected profile

Use `BANANAHUB_PROFILE=<name>` to select another persisted profile. Use `BANANAHUB_ENV_OVERRIDE=1` only for deliberate temporary environment overrides.

```json
{
  "default_profile": "gpt",
  "profiles": {
    "gpt": {
      "provider": "openai-compatible",
      "openai_base_url": "https://example.com/v1",
      "openai_api_key": "<persisted secret>",
      "model": "gpt-image-2"
    },
    "nano": {
      "provider": "google-ai-studio",
      "api_key": "<persisted secret>",
      "model": "gemini-3-pro-image-preview"
    }
  }
}
```

Default profile names:

- `gpt`: `openai-compatible` or `openai`
- `nano`: `google-ai-studio` or `gemini-compatible`
- `vertex`: `vertex-ai`
- `chat`: `chatgpt-compatible`

## Diagnosis Contract

`config doctor --json` returns fields agents should use directly:

- `status`: `ok` or `needs_setup`
- `provider` / `provider_label`
- `effective_config`: masked key, base URL, model, endpoint resolution, capabilities
- `resolved_from`: source of the active provider-scoped values only
- `ignored_config_sources`: configured env/profile values that are inactive for the selected provider
- `env_shadowed_config_sources`: env vars ignored because the selected persisted profile already defines that field
- `missing_fields`: `api_key`, `base_url`, `project`, `location`, etc.
- `missing_dependencies`: Python packages needed for the selected provider
- `dependency_install_command`: safe local command for installing missing Python packages
- `requires_user_secret`: true when the next step needs an API key
- `safe_to_autofix`: fields the agent may fill without seeing a secret
- `suggested_commands`: concrete next command(s)
- `suggested_commands_stdin`: variants that read API keys from stdin for direct agent entry
- `config_path`: persistent config file path, usually `~/.config/bananahub/config.json`
- `secret_entry_modes`: supported direct-entry, placeholder-command, and human-terminal fallback modes
- `agent_notes`: safety and quota reminders

Agent behavior:

- If `status=ok`, do not rerun setup; proceed to prompt optimization or generation.
- If `ignored_config_sources` is non-empty, do not ask the user about it unless it explains a failure.
- If only `base_url` is missing for the default `openai-compatible` path, ask for the endpoint URL or provide the quickset command with `<openai-compatible base url>`.
- If `requires_user_secret=true`, ask whether the user wants direct agent entry or a local placeholder command, then persist with `config quickset --api-key-stdin` when the agent receives the key.

## Validation Checklist

After setup:

```bash
python3 {baseDir}/scripts/bananahub.py init --skip-test --json
# optional dependency repair:
python3 {baseDir}/scripts/bananahub.py init --skip-test --install-deps
python3 {baseDir}/scripts/bananahub.py config show
```

If the user agrees to a provider call, run full init without `--skip-test`:

```bash
python3 {baseDir}/scripts/bananahub.py init --json
```

For OpenAI-compatible `gpt-image-2`, a generation smoke test is:

```bash
BANANAHUB_PROFILE=gpt python3 {baseDir}/scripts/bananahub.py generate \
  "Create a cute sticker of a tiny cheerful robot holding a banana, rounded kawaii vector style, thick clean outlines, soft pastel colors, plain white background, no text." \
  --model gpt-image-2 \
  --aspect 1:1 \
  --no-fallback \
  --output /tmp/bananahub-gpt-image-2-retry-test.png
```

Expected result: `status: "ok"`, `actual_model: "gpt-image-2"`, and a readable PNG. Telemetry `HTTP 403` is non-blocking and should not be mixed with generation failure.
