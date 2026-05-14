"""OpenAI Images API and OpenAI-compatible image adapter."""

import base64
import os

from .common import http_fetch_bytes, http_json_request, http_multipart_request, join_endpoint

DEFAULT_IMAGE_TIMEOUT_SECONDS = 900


def request_timeout(config=None, override=None, default=DEFAULT_IMAGE_TIMEOUT_SECONDS):
    if override is not None:
        try:
            return max(1, int(override))
        except (TypeError, ValueError):
            return default
    configured = (config or {}).get("BANANAHUB_IMAGE_TIMEOUT") or os.environ.get("BANANAHUB_IMAGE_TIMEOUT")
    if not configured:
        return default
    try:
        timeout = int(configured)
    except (TypeError, ValueError):
        return default
    return max(1, timeout)


def is_gpt_image_model(model):
    return str(model or "").strip().startswith("gpt-image")


def auth_headers(config, provider_openai="openai", default_provider="google-ai-studio"):
    provider = config.get("BANANAHUB_PROVIDER", default_provider)
    api_key = config.get("OPENAI_API_KEY", "") if provider == provider_openai else config.get("OPENAI_API_KEY") or config.get("GEMINI_API_KEY", "")
    return {"Authorization": f"Bearer {api_key}"}


def headers(config, provider_openai="openai", default_provider="google-ai-studio"):
    return {**auth_headers(config, provider_openai=provider_openai, default_provider=default_provider), "Content-Type": "application/json"}


def provider_base_url(config):
    return config.get("OPENAI_BASE_URL") or config.get("GOOGLE_GEMINI_BASE_URL") or "https://api.openai.com/v1"


def build_generation_payload(
    model,
    prompt,
    aspect_ratio,
    native_image_size=None,
    openai_size=None,
    quality=None,
    background=None,
    output_format=None,
    output_compression=None,
    n=None,
    moderation=None,
    user=None,
    response_format=None,
    provider=None,
):
    is_openai_compatible = provider == "openai-compatible"
    payload = {
        "model": model,
        "prompt": prompt,
    }
    if response_format:
        payload["response_format"] = response_format
    warnings = []

    if openai_size:
        payload["size"] = openai_size
    elif is_openai_compatible:
        payload["size"] = "auto"
    if quality:
        payload["quality"] = quality
    elif is_openai_compatible:
        payload["quality"] = "medium"
    if background:
        payload["background"] = background
    if output_format:
        payload["output_format"] = output_format
    elif is_openai_compatible:
        payload["output_format"] = "png"
    if output_compression is not None:
        payload["output_compression"] = output_compression
    if n is not None:
        payload["n"] = n
    if moderation:
        payload["moderation"] = moderation
    if user:
        payload["user"] = user

    if is_openai_compatible and aspect_ratio and aspect_ratio != "1:1":
        payload["extra_body"] = {"google": {"aspect_ratio": aspect_ratio}}

    if native_image_size:
        size_map = {
            "1K": "1024x1024",
            "2K": "2048x2048",
            "4K": "4096x4096",
        }
        if aspect_ratio and aspect_ratio != "1:1":
            warnings.append(
                f"`--image-size {native_image_size}` is ignored for openai-compatible generation when aspect ratio is not 1:1."
            )
        elif not openai_size and not is_openai_compatible:
            payload["size"] = size_map[native_image_size]

    return payload, warnings


def extract_images(response):
    items = response.get("data") if isinstance(response, dict) else None
    if not isinstance(items, list) or not items:
        return [], "No image generated. The endpoint returned an empty response."

    images = []
    errors = []
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            errors.append(f"Image {index}: invalid payload item.")
            continue
        b64_json = item.get("b64_json")
        if b64_json:
            try:
                images.append(base64.b64decode(b64_json))
            except Exception as exc:
                errors.append(f"Image {index}: failed to decode image bytes: {exc}")
            continue
        image_url = item.get("url")
        if image_url:
            images.append(http_fetch_bytes(image_url))
            continue
        errors.append(f"Image {index}: no image data found in response.")

    if images:
        return images, None
    return [], errors[0] if errors else "No image found in response."


def extract_image_bytes(response):
    images, error = extract_images(response)
    if error:
        return None, error
    return images[0], None


def list_models(config, resolve_endpoint, canonicalize_model, default_model, provider_openai="openai", default_provider="google-ai-studio"):
    endpoint_resolution = resolve_endpoint(provider_base_url(config))
    payload = http_json_request(
        "GET",
        join_endpoint(endpoint_resolution["resolved_base_url"], "models"),
        headers=headers(config, provider_openai=provider_openai, default_provider=default_provider),
    )
    entries = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return []

    models = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        raw_model_id = str(item.get("id", "")).strip()
        if not raw_model_id:
            continue
        model_id = canonicalize_model(raw_model_id.removeprefix("models/"))
        models.append({
            "id": model_id,
            "display_name": model_id,
            "description": f"owned_by={item.get('owned_by', 'unknown')}",
            "default": model_id == default_model,
        })
        if raw_model_id != model_id:
            models[-1]["aliases"] = [raw_model_id]
    return models


def try_generate(
    config,
    model,
    prompt,
    aspect_ratio,
    resolve_endpoint,
    image_size=None,
    openai_size=None,
    quality=None,
    background=None,
    output_format=None,
    output_compression=None,
    n=None,
    moderation=None,
    user=None,
    response_format=None,
    timeout=None,
    provider_openai="openai",
    default_provider="google-ai-studio",
):
    provider = config.get("BANANAHUB_PROVIDER", default_provider)
    payload, warnings = build_generation_payload(
        model,
        prompt,
        aspect_ratio,
        native_image_size=image_size,
        openai_size=openai_size,
        quality=quality,
        background=background,
        output_format=output_format,
        output_compression=output_compression,
        n=n,
        moderation=moderation,
        user=user,
        response_format=response_format,
        provider=provider,
    )
    endpoint_resolution = resolve_endpoint(provider_base_url(config))
    warnings = endpoint_resolution["warnings"] + warnings
    response = http_json_request(
        "POST",
        join_endpoint(endpoint_resolution["resolved_base_url"], "images/generations"),
        headers=headers(config, provider_openai=provider_openai, default_provider=default_provider),
        payload=payload,
        timeout=request_timeout(config, override=timeout),
    )
    images, error = extract_images(response)
    return images, warnings, error


def build_edit_fields(
    model,
    prompt,
    size=None,
    quality=None,
    background=None,
    output_format=None,
    output_compression=None,
    n=None,
    moderation=None,
    input_fidelity=None,
    user=None,
    response_format=None,
):
    fields = {
        "model": model,
        "prompt": prompt,
    }
    if response_format:
        fields["response_format"] = response_format
    if size:
        fields["size"] = size
    if quality:
        fields["quality"] = quality
    if background:
        fields["background"] = background
    if output_format:
        fields["output_format"] = output_format
    if output_compression is not None:
        fields["output_compression"] = output_compression
    if n is not None:
        fields["n"] = n
    if moderation:
        fields["moderation"] = moderation
    if input_fidelity:
        fields["input_fidelity"] = input_fidelity
    if user:
        fields["user"] = user
    return fields


def build_edit_files(input_path, ref_paths=None, mask_path=None):
    image_paths = [input_path, *(ref_paths or [])]
    image_field = "image[]" if len(image_paths) > 1 else "image"
    files = [{"field": image_field, "path": path} for path in image_paths]
    if mask_path:
        files.append({"field": "mask", "path": mask_path})
    return files


def try_edit(
    config,
    model,
    prompt,
    input_path,
    resolve_endpoint,
    ref_paths=None,
    mask_path=None,
    size=None,
    quality=None,
    background=None,
    output_format=None,
    output_compression=None,
    n=None,
    moderation=None,
    input_fidelity=None,
    user=None,
    response_format=None,
    timeout=None,
    provider_openai="openai",
    default_provider="google-ai-studio",
):
    endpoint_resolution = resolve_endpoint(provider_base_url(config))
    warnings = list(endpoint_resolution["warnings"])
    if input_fidelity and str(model or "").strip() == "gpt-image-2":
        warnings.append("`input_fidelity` is omitted for gpt-image-2 because the OpenAI API handles image inputs at high fidelity automatically.")
        input_fidelity = None
    fields = build_edit_fields(
        model,
        prompt,
        size=size,
        quality=quality,
        background=background,
        output_format=output_format,
        output_compression=output_compression,
        n=n,
        moderation=moderation,
        input_fidelity=input_fidelity,
        user=user,
        response_format=response_format,
    )
    files = build_edit_files(input_path, ref_paths=ref_paths, mask_path=mask_path)
    response = http_multipart_request(
        "POST",
        join_endpoint(endpoint_resolution["resolved_base_url"], "images/edits"),
        headers=auth_headers(config, provider_openai=provider_openai, default_provider=default_provider),
        fields=fields,
        files=files,
        timeout=request_timeout(config, override=timeout),
    )
    images, error = extract_images(response)
    return images, warnings, error
