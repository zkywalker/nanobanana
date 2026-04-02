#!/usr/bin/env python3
"""BananaHub - Gemini image generation CLI tool."""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def load_dotenv(env_path):
    """Parse a .env file into a dict."""
    config = {}
    if not env_path.exists():
        return config
    for line in env_path.read_text().strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


SKILL_CONFIG_PATH = Path.home() / ".config" / "bananahub" / "config.json"
LEGACY_SKILL_CONFIG_PATH = Path.home() / ".config" / "nanobanana" / "config.json"
LEGACY_ENV_PATH = Path.home() / ".gemini" / ".env"

# Mapping from config.json keys to internal config keys
CONFIG_KEY_MAP = {
    "api_key": "GEMINI_API_KEY",
    "base_url": "GOOGLE_GEMINI_BASE_URL",
}


def load_config(config_file=None):
    """Load API config with priority chain:
    1. Explicit --config file (JSON or .env)
    2. Environment variables
    3. Skill config: ~/.config/bananahub/config.json
    4. Legacy skill config: ~/.config/nanobanana/config.json
    5. Legacy .env:  ~/.gemini/.env
    """
    config = {}

    # Layer 5 (lowest): legacy ~/.gemini/.env
    config.update(load_dotenv(LEGACY_ENV_PATH))

    # Layer 4: legacy skill config ~/.config/nanobanana/config.json
    if LEGACY_SKILL_CONFIG_PATH.exists():
        try:
            data = json.loads(LEGACY_SKILL_CONFIG_PATH.read_text())
            for json_key, env_key in CONFIG_KEY_MAP.items():
                if json_key in data and data[json_key]:
                    config[env_key] = data[json_key]
        except (json.JSONDecodeError, KeyError):
            pass

    # Layer 3: preferred skill config ~/.config/bananahub/config.json
    if SKILL_CONFIG_PATH.exists():
        try:
            data = json.loads(SKILL_CONFIG_PATH.read_text())
            for json_key, env_key in CONFIG_KEY_MAP.items():
                if json_key in data and data[json_key]:
                    config[env_key] = data[json_key]
        except (json.JSONDecodeError, KeyError):
            pass

    # Layer 2: environment variables
    for env_key in ("GEMINI_API_KEY", "GOOGLE_GEMINI_BASE_URL"):
        val = os.environ.get(env_key)
        if val:
            config[env_key] = val

    # Layer 1 (highest): explicit --config file
    if config_file:
        cf = Path(config_file)
        if not cf.exists():
            print(json.dumps({"status": "error", "error": f"Config file not found: {cf}"}))
            sys.exit(1)
        if cf.suffix == ".json":
            try:
                data = json.loads(cf.read_text())
                for json_key, env_key in CONFIG_KEY_MAP.items():
                    if json_key in data and data[json_key]:
                        config[env_key] = data[json_key]
            except (json.JSONDecodeError, KeyError) as e:
                print(json.dumps({"status": "error", "error": f"Invalid JSON config: {e}"}))
                sys.exit(1)
        else:
            config.update(load_dotenv(cf))

    if not config.get("GEMINI_API_KEY"):
        sources = [
            f"  --config <file>",
            f"  env GEMINI_API_KEY",
            f"  {SKILL_CONFIG_PATH}",
            f"  {LEGACY_SKILL_CONFIG_PATH}",
            f"  {LEGACY_ENV_PATH}",
        ]
        print(json.dumps({
            "status": "error",
            "error": "GEMINI_API_KEY not found in any config source",
            "searched": sources,
        }, ensure_ascii=False))
        sys.exit(1)

    return config


def get_client(config):
    """Create Gemini client from config."""
    from google import genai

    api_key = config.get("GEMINI_API_KEY", "")
    base_url = config.get("GOOGLE_GEMINI_BASE_URL", "")

    if not api_key:
        print(json.dumps({"status": "error", "error": "GEMINI_API_KEY not found in config"}))
        sys.exit(1)

    http_options = {"api_version": "v1beta"}
    if base_url:
        http_options["base_url"] = base_url

    return genai.Client(api_key=api_key, http_options=http_options)


def cmd_init(args):
    """Check environment readiness and guide user through setup."""
    checks = []

    # 1. Check config sources
    config_sources = []
    if os.environ.get("GEMINI_API_KEY"):
        config_sources.append("env")
    if SKILL_CONFIG_PATH.exists():
        config_sources.append(str(SKILL_CONFIG_PATH))
    if LEGACY_SKILL_CONFIG_PATH.exists():
        config_sources.append(str(LEGACY_SKILL_CONFIG_PATH))
    if LEGACY_ENV_PATH.exists():
        config_sources.append(str(LEGACY_ENV_PATH))

    if config_sources:
        checks.append({"name": "config_source", "ok": True, "sources": config_sources})
    else:
        checks.append({"name": "config_source", "ok": False,
                        "error": f"No config found. Create {SKILL_CONFIG_PATH} or {LEGACY_ENV_PATH}"})

    # Try to load merged config (without exiting on failure)
    config = {}
    try:
        # Layer 4: legacy .env
        config.update(load_dotenv(LEGACY_ENV_PATH))
        # Layer 4: legacy skill config
        if LEGACY_SKILL_CONFIG_PATH.exists():
            try:
                data = json.loads(LEGACY_SKILL_CONFIG_PATH.read_text())
                for json_key, env_key in CONFIG_KEY_MAP.items():
                    if json_key in data and data[json_key]:
                        config[env_key] = data[json_key]
            except (json.JSONDecodeError, KeyError):
                pass
        # Layer 3: preferred skill config
        if SKILL_CONFIG_PATH.exists():
            try:
                data = json.loads(SKILL_CONFIG_PATH.read_text())
                for json_key, env_key in CONFIG_KEY_MAP.items():
                    if json_key in data and data[json_key]:
                        config[env_key] = data[json_key]
            except (json.JSONDecodeError, KeyError):
                pass
        # Layer 2: env vars
        for env_key in ("GEMINI_API_KEY", "GOOGLE_GEMINI_BASE_URL"):
            val = os.environ.get(env_key)
            if val:
                config[env_key] = val
    except Exception:
        pass

    # 2. Check API key
    api_key = config.get("GEMINI_API_KEY", "")
    if api_key:
        masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        checks.append({"name": "api_key", "ok": True, "value": masked})
    else:
        checks.append({"name": "api_key", "ok": False, "error": "GEMINI_API_KEY not found in any config source"})

    # 3. Check base URL
    base_url = config.get("GOOGLE_GEMINI_BASE_URL", "")
    if base_url:
        checks.append({"name": "base_url", "ok": True, "value": base_url})
    else:
        checks.append({"name": "base_url", "ok": True, "value": "(default Google endpoint)"})

    # 4. Check Python dependencies
    deps = {}
    for pkg, import_name in [("google-genai", "google.genai"), ("pillow", "PIL")]:
        try:
            __import__(import_name)
            deps[pkg] = True
        except ImportError:
            deps[pkg] = False
    checks.append({"name": "dependencies", "ok": all(deps.values()), "detail": deps})

    all_ok = all(c["ok"] for c in checks)

    # 5. API connectivity test (only if basic checks pass)
    if all_ok and not args.skip_test:
        try:
            client = get_client(config)
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents="Say OK",
            )
            text = ""
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        text = part.text
                        break
            checks.append({"name": "api_test", "ok": True, "response": text[:100]})
        except Exception as e:
            checks.append({"name": "api_test", "ok": False, "error": str(e)[:200]})

    all_ok = all(c["ok"] for c in checks)

    setup_guide = None
    if not all_ok:
        setup_guide = {
            "steps": [
                "Option A (recommended): Create skill config:",
                f"  1. mkdir -p {SKILL_CONFIG_PATH.parent}",
                f'  2. Create {SKILL_CONFIG_PATH} with:',
                '     {"api_key": "your_api_key_here", "base_url": "https://..."}',
                "Option B: Reuse legacy skill config path:",
                f"  1. mkdir -p {LEGACY_SKILL_CONFIG_PATH.parent}",
                f'  2. Create {LEGACY_SKILL_CONFIG_PATH} with:',
                '     {"api_key": "your_api_key_here", "base_url": "https://..."}',
                "Option C: Create legacy .env:",
                f"  1. mkdir -p {LEGACY_ENV_PATH.parent}",
                f"  2. Create {LEGACY_ENV_PATH} with:",
                "     GEMINI_API_KEY=your_api_key_here",
                "     GOOGLE_GEMINI_BASE_URL=https://...  (optional)",
                "Option D: Set environment variables:",
                "  export GEMINI_API_KEY=your_api_key_here",
                "",
                "Get your API key from: https://aistudio.google.com/apikey",
                "Install dependencies: pip install google-genai pillow",
                f"Run again: python3 bananahub.py init",
            ]
        }

    print(json.dumps({
        "status": "ok" if all_ok else "incomplete",
        "checks": checks,
        "setup_guide": setup_guide,
    }, ensure_ascii=False, indent=2))

    if not all_ok:
        sys.exit(1)


IMAGE_KEYWORDS = {"image", "imagen"}
DEFAULT_MODEL = "gemini-3-pro-image-preview"
MODEL_ALIASES = {
    "nano-banana-pro-preview": "gemini-3-pro-image-preview",
}
NATIVE_IMAGE_SIZES = ("1K", "2K", "4K")

# Ordered fallback chain: try these models in sequence when the requested model fails
MODEL_FALLBACK_CHAIN = [
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image",
    # Keep the old model as the final legacy fallback for older accounts.
    "gemini-2.0-flash-preview-image-generation",
]

# HTTP status codes that trigger fallback (server-side, not user's fault)
FALLBACK_STATUS_CODES = {"500", "502", "503", "504", "UNAVAILABLE", "INTERNAL", "OVERLOADED"}

FALLBACK_MODELS = [
    {"id": "gemini-3-pro-image-preview", "display_name": "Gemini 3 Pro Image Preview", "default": True},
    {"id": "gemini-3.1-flash-image-preview", "display_name": "Gemini 3.1 Flash Image Preview", "default": False},
    {"id": "gemini-2.5-flash-image", "display_name": "Gemini 2.5 Flash Image", "default": False},
    {"id": "gemini-2.0-flash-preview-image-generation", "display_name": "Gemini 2.0 Flash Image Generation", "default": False},
]


def _canonicalize_model(model):
    """Map known aliases to the canonical model id used by the runtime."""
    return MODEL_ALIASES.get((model or "").strip(), (model or "").strip())


def _dedupe_preserve_order(items):
    """Keep the first occurrence of each item while preserving order."""
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _normalize_image_size(value):
    """Normalize native image-size presets accepted by Gemini image models."""
    if not value:
        return None
    normalized = value.strip().upper()
    if normalized in NATIVE_IMAGE_SIZES:
        return normalized
    return None


def _parse_resize_dims(value):
    """Parse post-processing resize dimensions in WxH form."""
    if not value:
        return None
    match = re.fullmatch(r"(\d+)x(\d+)", value.strip().lower())
    if not match:
        return None
    width, height = map(int, match.groups())
    if width <= 0 or height <= 0:
        return None
    return width, height


def _resolve_image_request_options(args):
    """Resolve native image-size vs legacy/post-processing resize flags."""
    native_image_size = None
    resize_dims = None
    warnings = []

    explicit_image_size = getattr(args, "image_size", None)
    if explicit_image_size:
        native_image_size = _normalize_image_size(explicit_image_size)
        if not native_image_size:
            supported = ", ".join(NATIVE_IMAGE_SIZES)
            raise ValueError(
                f"Invalid --image-size value: {explicit_image_size}. "
                f"Use one of: {supported}."
            )

    explicit_resize = getattr(args, "resize", None)
    if explicit_resize:
        resize_dims = _parse_resize_dims(explicit_resize)
        if not resize_dims:
            raise ValueError(
                f"Invalid --resize value: {explicit_resize}. Use WxH, for example 1024x1024."
            )

    legacy_size = getattr(args, "size", None)
    if legacy_size:
        legacy_native_size = _normalize_image_size(legacy_size)
        legacy_resize_dims = _parse_resize_dims(legacy_size)
        if legacy_native_size:
            if native_image_size and native_image_size != legacy_native_size:
                raise ValueError(
                    f"Conflicting native size values: --image-size {native_image_size} and --size {legacy_size}."
                )
            native_image_size = native_image_size or legacy_native_size
            warnings.append(
                f"`--size {legacy_size}` is treated as a native image-size preset. Prefer `--image-size {legacy_size}`."
            )
        elif legacy_resize_dims:
            if resize_dims and resize_dims != legacy_resize_dims:
                raise ValueError(
                    f"Conflicting resize values: --resize {explicit_resize} and --size {legacy_size}."
                )
            resize_dims = resize_dims or legacy_resize_dims
            warnings.append(
                f"`--size {legacy_size}` is treated as post-processing resize. Prefer `--resize {legacy_size}`."
            )
        else:
            supported = ", ".join(NATIVE_IMAGE_SIZES)
            raise ValueError(
                f"Invalid --size value: {legacy_size}. Use one of {supported} for native image size "
                "or WxH for post-processing resize."
            )

    return native_image_size, resize_dims, warnings


def _is_server_error(exception):
    """Check if an exception is a server-side error eligible for fallback."""
    msg = str(exception).upper()
    return any(code in msg for code in FALLBACK_STATUS_CODES)


def _get_fallback_models(current_model):
    """Return fallback models to try after current_model fails.
    If current_model is in the chain, return everything after it.
    If not in the chain, return the full chain (skipping current_model if present).
    """
    current_model = _canonicalize_model(current_model)
    if current_model in MODEL_FALLBACK_CHAIN:
        idx = MODEL_FALLBACK_CHAIN.index(current_model)
        return MODEL_FALLBACK_CHAIN[idx + 1:]
    return [m for m in MODEL_FALLBACK_CHAIN if m != current_model]


def cmd_models(args):
    """List available image generation models from the API, with fallback."""
    config = load_config(getattr(args, "config", None))
    try:
        client = get_client(config)
        api_models = {}
        for m in client.models.list(config={"page_size": 100}):
            name = m.name or ""
            # Strip "models/" prefix if present
            raw_model_id = name.removeprefix("models/")
            model_id = _canonicalize_model(raw_model_id)
            desc = (m.description or "").lower()
            model_id_lower = raw_model_id.lower()
            display = m.display_name or model_id

            # Filter: model id or description mentions image-related keywords
            is_image = any(kw in model_id_lower for kw in IMAGE_KEYWORDS) or any(kw in desc for kw in IMAGE_KEYWORDS)
            if not is_image:
                continue

            existing = api_models.get(model_id)
            if existing:
                if raw_model_id != model_id:
                    existing.setdefault("aliases", [])
                    if raw_model_id not in existing["aliases"]:
                        existing["aliases"].append(raw_model_id)
                continue

            entry = {
                "id": model_id,
                "display_name": display,
                "description": (m.description or "")[:120],
                "input_token_limit": getattr(m, "input_token_limit", None),
                "output_token_limit": getattr(m, "output_token_limit", None),
                "default": model_id == DEFAULT_MODEL,
            }
            if raw_model_id != model_id:
                entry["aliases"] = [raw_model_id]
            api_models[model_id] = entry

        if api_models:
            # Sort: default model first, then alphabetically
            models = sorted(api_models.values(), key=lambda x: (not x["default"], x["id"]))
            print(json.dumps({"status": "ok", "source": "api", "models": models}, ensure_ascii=False))
            return

        # API returned no image models — use fallback
        print(json.dumps({"status": "ok", "source": "fallback", "models": FALLBACK_MODELS}, ensure_ascii=False))

    except Exception as e:
        # API call failed — use fallback
        print(json.dumps({
            "status": "ok",
            "source": "fallback",
            "warning": f"API query failed: {str(e)[:150]}",
            "models": FALLBACK_MODELS,
        }, ensure_ascii=False))


def _try_edit(client, model, prompt, input_images, image_size=None):
    """Attempt image editing with a single model. Returns (image_part, text_parts, None) or (None, [], error_str).

    Args:
        input_images: list of PIL Image objects (main image + optional reference images).
    """
    from google.genai import types

    contents = [prompt] + input_images
    image_config = types.ImageConfig(image_size=image_size) if image_size else None
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=image_config,
        ),
    )

    if not response.candidates or not response.candidates[0].content.parts:
        return None, [], "No response generated. The model may have refused the prompt due to content policy."

    image_part = None
    text_parts = []
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            image_part = part
        elif hasattr(part, "text") and part.text:
            text_parts.append(part.text)

    if not image_part:
        error_msg = "No image in response."
        if text_parts:
            error_msg += f" Model said: {' '.join(text_parts)}"
        return None, text_parts, error_msg

    return image_part, text_parts, None


def cmd_edit(args):
    """Edit an existing image based on a text prompt, with automatic model fallback."""
    import io

    try:
        native_image_size, resize_dims, option_warnings = _resolve_image_request_options(args)
    except ValueError as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    # Validate input image before importing heavy dependencies
    input_path = Path(args.input)
    if not input_path.exists():
        print(json.dumps({
            "status": "error",
            "error": f"Input image not found: {input_path}",
        }, ensure_ascii=False))
        sys.exit(1)

    # Validate reference images
    ref_paths = []
    for ref in (args.ref or []):
        rp = Path(ref)
        if not rp.exists():
            print(json.dumps({
                "status": "error",
                "error": f"Reference image not found: {rp}",
            }, ensure_ascii=False))
            sys.exit(1)
        ref_paths.append(rp)

    if len(ref_paths) > 13:
        print(json.dumps({
            "status": "error",
            "error": f"Too many reference images: {len(ref_paths)}. Maximum is 13 reference images.",
        }, ensure_ascii=False))
        sys.exit(1)

    if 1 + len(ref_paths) > 14:
        print(json.dumps({
            "status": "error",
            "error": f"Too many input images: {1 + len(ref_paths)}. Total images (input + refs) must be 14 or fewer.",
        }, ensure_ascii=False))
        sys.exit(1)

    from PIL import Image

    # Load all images: main input + references
    input_images = []
    try:
        input_images.append(Image.open(str(input_path)))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": f"Cannot read input image: {e}",
        }, ensure_ascii=False))
        sys.exit(1)

    for rp in ref_paths:
        try:
            input_images.append(Image.open(str(rp)))
        except Exception as e:
            print(json.dumps({
                "status": "error",
                "error": f"Cannot read reference image {rp}: {e}",
            }, ensure_ascii=False))
            sys.exit(1)

    config_data = load_config(getattr(args, "config", None))
    client = get_client(config_data)

    requested_model_input = args.model or DEFAULT_MODEL
    requested_model = _canonicalize_model(requested_model_input)
    prompt = args.prompt
    no_fallback = getattr(args, "no_fallback", False)
    retries = getattr(args, "retries", 1)

    # Determine output path (deferred until model is known)
    user_output = args.output

    # Build model attempt list
    if no_fallback:
        models_to_try = [requested_model]
    else:
        models_to_try = _dedupe_preserve_order([requested_model] + _get_fallback_models(requested_model))

    tried = []
    last_error = None

    for model in models_to_try:
        for attempt in range(1 + retries):
            try:
                image_part, text_parts, gen_error = _try_edit(
                    client,
                    model,
                    prompt,
                    input_images,
                    image_size=native_image_size,
                )

                if gen_error:
                    print(json.dumps({
                        "status": "error",
                        "error": gen_error,
                        "prompt": prompt,
                        "requested_model": requested_model_input,
                        "actual_model": model,
                    }, ensure_ascii=False))
                    sys.exit(1)

                # Success — resolve output path now that we know the actual model
                if user_output:
                    output_path = Path(user_output)
                else:
                    output_dir = Path.cwd()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    model_short = model.replace("gemini-", "").replace("-preview", "").replace("-image-generation", "")
                    output_path = output_dir / f"bananahub_edit_{model_short}_{timestamp}.png"

                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Save image
                image = Image.open(io.BytesIO(image_part.inline_data.data))

                if resize_dims:
                    image = image.resize(resize_dims, Image.LANCZOS)

                image.save(str(output_path), "PNG")

                result = {
                    "status": "ok",
                    "file": str(output_path),
                    "input": str(input_path),
                    "requested_model": requested_model_input,
                    "actual_model": model,
                    "prompt": prompt,
                    "image_size": f"{image.width}x{image.height}",
                    "total_images": len(input_images),
                }
                if requested_model_input != requested_model:
                    result["resolved_requested_model"] = requested_model
                if native_image_size:
                    result["native_image_size"] = native_image_size
                if resize_dims:
                    result["post_resize"] = f"{resize_dims[0]}x{resize_dims[1]}"
                if option_warnings:
                    result["warnings"] = option_warnings
                if ref_paths:
                    result["ref_images"] = [str(rp) for rp in ref_paths]
                if model != requested_model:
                    result["fallback_from"] = requested_model
                result["fallback_chain"] = models_to_try
                result["models_tried"] = tried + [model]
                if text_parts:
                    result["model_text"] = " ".join(text_parts)
                print(json.dumps(result, ensure_ascii=False))
                return

            except Exception as e:
                last_error = e
                if not _is_server_error(e):
                    tried.append({"model": model, "error": str(e)[:150]})
                    break
                if attempt < retries:
                    import time
                    delay = 2 ** (attempt + 1)
                    tried.append({"model": model, "error": str(e)[:150], "retry": attempt + 1, "delay_s": delay})
                    time.sleep(delay)
                else:
                    tried.append({"model": model, "error": str(e)[:150]})
        else:
            continue
        break

    # All models failed
    error_msg = str(last_error)
    hint = ""
    if "SAFETY" in error_msg.upper() or "BLOCKED" in error_msg.upper():
        hint = "Content was blocked by safety filters. Try rephrasing the prompt."
    elif "QUOTA" in error_msg.upper() or "429" in error_msg:
        hint = "API quota exceeded. Wait a moment and try again."
    elif "401" in error_msg or "403" in error_msg:
        hint = "Authentication failed. Check your GEMINI_API_KEY config."
    elif "TIMEOUT" in error_msg.upper() or "CONNECT" in error_msg.upper():
        hint = "Network error. Check your connection and base_url config."

    result = {
        "status": "error",
        "error": error_msg,
        "prompt": prompt,
        "requested_model": requested_model_input,
        "resolved_requested_model": requested_model,
        "retries_per_model": retries,
        "fallback_chain": models_to_try,
        "models_tried": tried,
    }
    if native_image_size:
        result["native_image_size"] = native_image_size
    if resize_dims:
        result["post_resize"] = f"{resize_dims[0]}x{resize_dims[1]}"
    if option_warnings:
        result["warnings"] = option_warnings
    if hint:
        result["hint"] = hint
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(1)


def _try_generate(client, model, prompt, aspect_ratio, image_size=None):
    """Attempt image generation with a single model. Returns (image_part, None) or (None, error_str)."""
    from google.genai import types

    image_config_kwargs = {"aspect_ratio": aspect_ratio}
    if image_size:
        image_config_kwargs["image_size"] = image_size

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(**image_config_kwargs),
        ),
    )

    if not response.candidates or not response.candidates[0].content.parts:
        return None, "No image generated. The model may have refused the prompt due to content policy."

    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            return part, None

    text_parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, "text") and p.text]
    error_msg = "No image in response."
    if text_parts:
        error_msg += f" Model said: {' '.join(text_parts)}"
    return None, error_msg


def cmd_generate(args):
    """Generate an image from a text prompt, with automatic model fallback."""
    from PIL import Image
    import io

    try:
        native_image_size, resize_dims, option_warnings = _resolve_image_request_options(args)
    except ValueError as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    config = load_config(getattr(args, "config", None))
    client = get_client(config)

    requested_model_input = args.model or DEFAULT_MODEL
    requested_model = _canonicalize_model(requested_model_input)
    prompt = args.prompt
    aspect_ratio = args.aspect or "1:1"
    no_fallback = getattr(args, "no_fallback", False)
    retries = getattr(args, "retries", 1)

    # Determine output path (default: current working directory with model name)
    user_output = args.output

    # Build model attempt list
    if no_fallback:
        models_to_try = [requested_model]
    else:
        models_to_try = _dedupe_preserve_order([requested_model] + _get_fallback_models(requested_model))

    tried = []
    last_error = None

    for model in models_to_try:
        # Retry same model up to (1 + retries) times before fallback
        for attempt in range(1 + retries):
            try:
                image_part, gen_error = _try_generate(
                    client,
                    model,
                    prompt,
                    aspect_ratio,
                    image_size=native_image_size,
                )

                if gen_error:
                    # Content policy / no image — not a server error, don't fallback
                    print(json.dumps({
                        "status": "error",
                        "error": gen_error,
                        "prompt": prompt,
                        "requested_model": requested_model_input,
                        "actual_model": model,
                    }, ensure_ascii=False))
                    sys.exit(1)

                # Success — resolve output path now that we know the actual model
                if user_output:
                    output_path = Path(user_output)
                else:
                    output_dir = Path.cwd()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    model_short = model.replace("gemini-", "").replace("-preview", "").replace("-image-generation", "")
                    output_path = output_dir / f"bananahub_{model_short}_{timestamp}.png"

                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Save image
                image = Image.open(io.BytesIO(image_part.inline_data.data))

                if resize_dims:
                    image = image.resize(resize_dims, Image.LANCZOS)

                image.save(str(output_path), "PNG")

                result = {
                    "status": "ok",
                    "file": str(output_path),
                    "requested_model": requested_model_input,
                    "actual_model": model,
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "image_size": f"{image.width}x{image.height}",
                }
                if requested_model_input != requested_model:
                    result["resolved_requested_model"] = requested_model
                if native_image_size:
                    result["native_image_size"] = native_image_size
                if resize_dims:
                    result["post_resize"] = f"{resize_dims[0]}x{resize_dims[1]}"
                if option_warnings:
                    result["warnings"] = option_warnings
                if model != requested_model:
                    result["fallback_from"] = requested_model
                result["fallback_chain"] = models_to_try
                result["models_tried"] = tried + [model]
                print(json.dumps(result, ensure_ascii=False))
                return

            except Exception as e:
                last_error = e
                if not _is_server_error(e):
                    tried.append({"model": model, "error": str(e)[:150]})
                    break
                # Retry same model with exponential backoff
                if attempt < retries:
                    import time
                    delay = 2 ** (attempt + 1)
                    tried.append({"model": model, "error": str(e)[:150], "retry": attempt + 1, "delay_s": delay})
                    time.sleep(delay)
                else:
                    tried.append({"model": model, "error": str(e)[:150]})
        else:
            # Inner loop completed without break — all retries exhausted, try next model
            continue
        # Inner loop was broken (non-server error) — stop trying
        break

    # All models failed
    error_msg = str(last_error)
    hint = ""
    if "SAFETY" in error_msg.upper() or "BLOCKED" in error_msg.upper():
        hint = "Content was blocked by safety filters. Try rephrasing the prompt."
    elif "QUOTA" in error_msg.upper() or "429" in error_msg:
        hint = "API quota exceeded. Wait a moment and try again."
    elif "401" in error_msg or "403" in error_msg:
        hint = "Authentication failed. Check your GEMINI_API_KEY config."
    elif "TIMEOUT" in error_msg.upper() or "CONNECT" in error_msg.upper():
        hint = "Network error. Check your connection and base_url config."

    result = {
        "status": "error",
        "error": error_msg,
        "prompt": prompt,
        "requested_model": requested_model_input,
        "resolved_requested_model": requested_model,
        "retries_per_model": retries,
        "fallback_chain": models_to_try,
        "models_tried": tried,
    }
    if native_image_size:
        result["native_image_size"] = native_image_size
    if resize_dims:
        result["post_resize"] = f"{resize_dims[0]}x{resize_dims[1]}"
    if option_warnings:
        result["warnings"] = option_warnings
    if hint:
        result["hint"] = hint
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(prog="bananahub.py", description="BananaHub - Gemini image generation")
    parser.add_argument("--config", help="Path to config file (JSON or .env)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate an image from a prompt")
    gen_parser.add_argument("prompt", help="Text prompt for image generation")
    gen_parser.add_argument("--model", "-m", help="Model ID (default: gemini-3-pro-image-preview)")
    gen_parser.add_argument("--aspect", "-a", help="Aspect ratio, e.g. 1:1, 16:9, 9:16 (default: 1:1)")
    gen_parser.add_argument("--image-size", help="Native image-size preset: 1K, 2K, or 4K")
    gen_parser.add_argument("--resize", help="Post-process resize to WxH, e.g. 1024x1024")
    gen_parser.add_argument("--size", "-s", help="Legacy compatibility flag: use 1K/2K/4K for native image size, or WxH for post-processing resize")
    gen_parser.add_argument("--output", "-o", help="Output file path (default: current directory)")
    gen_parser.add_argument("--no-fallback", action="store_true", help="Disable automatic model fallback on server errors")
    gen_parser.add_argument("--retries", type=int, default=1, help="Retry count per model on 503 before fallback (default: 1)")

    # edit command
    edit_parser = subparsers.add_parser("edit", help="Edit an existing image with a text prompt")
    edit_parser.add_argument("prompt", help="Text prompt describing the edit")
    edit_parser.add_argument("--input", "-i", required=True, help="Path to the source image")
    edit_parser.add_argument("--ref", "-r", nargs="+", default=[], help="Reference image paths (up to 13 additional images for style/content guidance)")
    edit_parser.add_argument("--model", "-m", help="Model ID (default: gemini-3-pro-image-preview)")
    edit_parser.add_argument("--image-size", help="Native image-size preset: 1K, 2K, or 4K")
    edit_parser.add_argument("--resize", help="Post-process resize to WxH, e.g. 1024x1024")
    edit_parser.add_argument("--size", "-s", help="Legacy compatibility flag: use 1K/2K/4K for native image size, or WxH for post-processing resize")
    edit_parser.add_argument("--output", "-o", help="Output file path (default: current directory)")
    edit_parser.add_argument("--no-fallback", action="store_true", help="Disable automatic model fallback on server errors")
    edit_parser.add_argument("--retries", type=int, default=1, help="Retry count per model on 503 before fallback (default: 1)")

    # models command
    subparsers.add_parser("models", help="List available models")

    # init command
    init_parser = subparsers.add_parser("init", help="Check environment and guide setup")
    init_parser.add_argument("--skip-test", action="store_true", help="Skip API connectivity test")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "edit":
        cmd_edit(args)
    elif args.command == "models":
        cmd_models(args)
    elif args.command == "init":
        cmd_init(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
