"""OpenAI Images API and OpenAI-compatible image adapter."""

import base64

from .common import http_fetch_bytes, http_json_request, http_multipart_request, join_endpoint


def auth_headers(config, provider_openai="openai", default_provider="google-ai-studio"):
    provider = config.get("BANANAHUB_PROVIDER", default_provider)
    api_key = config.get("OPENAI_API_KEY", "") if provider == provider_openai else config.get("GEMINI_API_KEY", "")
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
    provider=None,
):
    is_openai_compatible = provider == "openai-compatible"
    payload = {
        "model": model,
        "prompt": prompt,
    }
    if not is_openai_compatible:
        payload["response_format"] = "b64_json"
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

    if aspect_ratio and aspect_ratio != "1:1":
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


def extract_image_bytes(response):
    items = response.get("data") if isinstance(response, dict) else None
    if not isinstance(items, list) or not items:
        return None, "No image generated. The endpoint returned an empty response."
    first = items[0]
    if not isinstance(first, dict):
        return None, "No image generated. The endpoint returned an invalid payload."
    b64_json = first.get("b64_json")
    if b64_json:
        try:
            return base64.b64decode(b64_json), None
        except Exception as exc:
            return None, f"Failed to decode image bytes: {exc}"
    image_url = first.get("url")
    if image_url:
        return http_fetch_bytes(image_url), None
    return None, "No image found in response."


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


def try_generate(config, model, prompt, aspect_ratio, resolve_endpoint, image_size=None, openai_size=None, quality=None, background=None, output_format=None, output_compression=None, provider_openai="openai", default_provider="google-ai-studio"):
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
        provider=provider,
    )
    endpoint_resolution = resolve_endpoint(provider_base_url(config))
    warnings = endpoint_resolution["warnings"] + warnings
    response = http_json_request(
        "POST",
        join_endpoint(endpoint_resolution["resolved_base_url"], "images/generations"),
        headers=headers(config, provider_openai=provider_openai, default_provider=default_provider),
        payload=payload,
        timeout=120,
    )
    image_bytes, error = extract_image_bytes(response)
    return image_bytes, warnings, error


def try_edit(config, model, prompt, input_path, resolve_endpoint, ref_paths=None, mask_path=None, size=None, provider_openai="openai", default_provider="google-ai-studio"):
    endpoint_resolution = resolve_endpoint(provider_base_url(config))
    fields = {
        "model": model,
        "prompt": prompt,
        "response_format": "b64_json",
    }
    if size:
        fields["size"] = size
    files = [{"field": "image", "path": input_path}]
    for ref_path in ref_paths or []:
        files.append({"field": "image", "path": ref_path})
    if mask_path:
        files.append({"field": "mask", "path": mask_path})
    response = http_multipart_request(
        "POST",
        join_endpoint(endpoint_resolution["resolved_base_url"], "images/edits"),
        headers=auth_headers(config, provider_openai=provider_openai, default_provider=default_provider),
        fields=fields,
        files=files,
        timeout=120,
    )
    image_bytes, error = extract_image_bytes(response)
    return image_bytes, endpoint_resolution["warnings"], error
