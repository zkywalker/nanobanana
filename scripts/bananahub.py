#!/usr/bin/env python3
"""BananaHub - provider-backed image generation CLI tool."""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib import error as urlerror, request as urlrequest
from uuid import uuid4

try:
    from providers import chatgpt_compatible as chatgpt_provider
    import config_store
    from providers import gemini as gemini_provider
    from providers import openai_images as openai_provider
    import runtime_config as runtime_cfg
    from providers.common import (
        extract_error_message_from_payload as provider_extract_error_message_from_payload,
        http_fetch_bytes as provider_http_fetch_bytes,
        http_json_request as provider_http_json_request,
        http_multipart_request as provider_http_multipart_request,
        join_endpoint as provider_join_endpoint,
    )
except ImportError:  # pragma: no cover - supports direct import from tests with explicit module path
    from scripts.providers import chatgpt_compatible as chatgpt_provider
    from scripts import config_store
    from scripts.providers import gemini as gemini_provider
    from scripts.providers import openai_images as openai_provider
    from scripts import runtime_config as runtime_cfg
    from scripts.providers.common import (
        extract_error_message_from_payload as provider_extract_error_message_from_payload,
        http_fetch_bytes as provider_http_fetch_bytes,
        http_json_request as provider_http_json_request,
        http_multipart_request as provider_http_multipart_request,
        join_endpoint as provider_join_endpoint,
    )


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


SKILL_CONFIG_DIR = runtime_cfg.SKILL_CONFIG_DIR
SKILL_CONFIG_PATH = runtime_cfg.SKILL_CONFIG_PATH
TELEMETRY_STATE_PATH = runtime_cfg.TELEMETRY_STATE_PATH
HUB_API_BASE = os.environ.get("BANANAHUB_HUB_API", "https://worker.bananahub.ai/api")
DEFAULT_TEMPLATE_REPO = "bananahub-ai/bananahub-skill"
DEFAULT_PROMPT_ARCHIVE_DIR = "bananahub-prompts"
VALID_TEMPLATE_DISTRIBUTIONS = {"bundled", "remote"}
VALID_CATALOG_SOURCES = {"curated", "discovered"}
VALID_TELEMETRY_EVENTS = {"selected", "generate_success", "edit_success"}

PROVIDER_GOOGLE_AI_STUDIO = runtime_cfg.PROVIDER_GOOGLE_AI_STUDIO
PROVIDER_GEMINI_COMPATIBLE = runtime_cfg.PROVIDER_GEMINI_COMPATIBLE
PROVIDER_VERTEX_AI = runtime_cfg.PROVIDER_VERTEX_AI
PROVIDER_OPENAI = runtime_cfg.PROVIDER_OPENAI
PROVIDER_OPENAI_COMPATIBLE = runtime_cfg.PROVIDER_OPENAI_COMPATIBLE
PROVIDER_CHATGPT_COMPATIBLE = runtime_cfg.PROVIDER_CHATGPT_COMPATIBLE
SUPPORTED_PROVIDERS = runtime_cfg.SUPPORTED_PROVIDERS
SUPPORTED_RUNTIME_PROVIDERS = runtime_cfg.SUPPORTED_RUNTIME_PROVIDERS
DEFAULT_PROVIDER = runtime_cfg.DEFAULT_PROVIDER
DEFAULT_LOCATION = runtime_cfg.DEFAULT_LOCATION

TRANSPORT_GENAI = runtime_cfg.TRANSPORT_GENAI
TRANSPORT_GEMINI_REST = runtime_cfg.TRANSPORT_GEMINI_REST
TRANSPORT_OPENAI_REST = runtime_cfg.TRANSPORT_OPENAI_REST
SUPPORTED_TRANSPORTS = runtime_cfg.SUPPORTED_TRANSPORTS

AUTH_MODE_API_KEY = runtime_cfg.AUTH_MODE_API_KEY
AUTH_MODE_ADC = runtime_cfg.AUTH_MODE_ADC
SUPPORTED_AUTH_MODES = runtime_cfg.SUPPORTED_AUTH_MODES

PROVIDER_ALIASES = runtime_cfg.PROVIDER_ALIASES
TRANSPORT_ALIASES = runtime_cfg.TRANSPORT_ALIASES
AUTH_MODE_ALIASES = runtime_cfg.AUTH_MODE_ALIASES
DEFAULT_TRANSPORT_BY_PROVIDER = runtime_cfg.DEFAULT_TRANSPORT_BY_PROVIDER
CONFIG_KEY_MAP = runtime_cfg.CONFIG_KEY_MAP
ENV_KEY_ALIASES = runtime_cfg.ENV_KEY_ALIASES

def _mask_secret(value):
    """Return a masked representation for API keys."""
    return runtime_cfg.mask_secret(value)


def _normalize_base_url(value):
    """Normalize a custom base URL for provider endpoints."""
    return runtime_cfg.normalize_base_url(value)

def _split_trailing_api_version(base_url, default_api_version="v1beta"):
    """Split a trailing API version suffix from a base URL when present."""
    return runtime_cfg.split_trailing_api_version(base_url, default_api_version=default_api_version)

def _resolve_genai_endpoint(base_url):
    """Resolve a Gemini-style endpoint into base_url + api_version parts."""
    return runtime_cfg.resolve_genai_endpoint(base_url)

def _resolve_openai_endpoint(base_url):
    """Resolve an OpenAI-compatible endpoint into the URL used by runtime calls."""
    return runtime_cfg.resolve_openai_endpoint(base_url)

def _normalize_provider(value):
    """Normalize provider ids accepted by BananaHub config."""
    return runtime_cfg.normalize_provider(value)

def _normalize_transport(value):
    """Normalize transport ids accepted by BananaHub config."""
    return runtime_cfg.normalize_transport(value)

def _normalize_auth_mode(value):
    """Normalize auth-mode values accepted by BananaHub config."""
    return runtime_cfg.normalize_auth_mode(value)

def _normalize_model(value):
    """Normalize optional default model ids."""
    if value is None:
        return None

    normalized = str(value).strip()
    if not normalized:
        return None
    return _canonicalize_model(normalized)


def _is_truthy(value):
    """Return True for common truthy env/config values."""
    return runtime_cfg.is_truthy(value)


def _active_api_key(config, runtime_support=None):
    """Return the key used by the currently selected provider, plus config key metadata."""
    support = runtime_support or _runtime_support_status(config)
    if support["auth_mode"] != AUTH_MODE_API_KEY:
        return None, None, "not_required"

    provider = support["provider"]
    if provider == PROVIDER_CHATGPT_COMPATIBLE:
        return config.get("BANANAHUB_CHATGPT_API_KEY", ""), "BANANAHUB_CHATGPT_API_KEY", "chatgpt"
    if provider == PROVIDER_OPENAI:
        return config.get("OPENAI_API_KEY", ""), "OPENAI_API_KEY", "openai"
    if provider == PROVIDER_OPENAI_COMPATIBLE and config.get("OPENAI_API_KEY"):
        return config.get("OPENAI_API_KEY", ""), "OPENAI_API_KEY", "openai-compatible"
    return config.get("GEMINI_API_KEY", ""), "GEMINI_API_KEY", "gemini"


def _host_imagegen_available(args=None):
    """Return whether the caller tells BananaHub that host-native image generation exists."""
    if args and getattr(args, "host_imagegen", False):
        return True
    return _is_truthy(os.environ.get("BANANAHUB_HOST_IMAGEGEN", ""))

def _normalize_config_value(env_key, value):
    """Normalize raw config values based on the canonical internal key."""
    return config_store.normalize_config_value(env_key, value, _canonicalize_model)

def _read_json_file(path, required=False):
    """Read a JSON file and return a dict."""
    return config_store.read_json_file(path, required=required)

def _write_json_file(path, data):
    """Write JSON with stable formatting."""
    return config_store.write_json_file(path, data)

def _normalize_template_repo(value):
    """Normalize template repo values."""
    normalized = str(value or "").strip()
    if not normalized or "/" not in normalized:
        return DEFAULT_TEMPLATE_REPO
    return normalized


def _normalize_template_distribution(value):
    """Normalize bundled vs remote template distribution values."""
    normalized = str(value or "").strip().lower()
    if not normalized:
        return ""
    if normalized not in VALID_TEMPLATE_DISTRIBUTIONS:
        raise ValueError("template distribution must be bundled or remote")
    return normalized


def _normalize_catalog_source(value):
    """Normalize curated vs discovered catalog source values."""
    normalized = str(value or "").strip().lower()
    if not normalized:
        return ""
    if normalized not in VALID_CATALOG_SOURCES:
        raise ValueError("template source must be curated or discovered")
    return normalized


def _normalize_telemetry_event(value):
    """Validate telemetry event names accepted by the Hub API."""
    normalized = str(value or "").strip().lower()
    if normalized not in VALID_TELEMETRY_EVENTS:
        supported = ", ".join(sorted(VALID_TELEMETRY_EVENTS))
        raise ValueError(f"invalid telemetry event: {value}. Use one of: {supported}")
    return normalized


def _telemetry_disabled():
    """Allow local opt-out via environment flag."""
    raw = str(os.environ.get("BANANAHUB_DISABLE_TELEMETRY", "")).strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _load_telemetry_state(create=False):
    """Load or create local anonymous telemetry identity."""
    state = _read_json_file(TELEMETRY_STATE_PATH)
    if not isinstance(state, dict):
        state = {}

    anonymous_id = str(state.get("anonymous_id", "")).strip()
    if anonymous_id:
        return state

    if not create:
        return state

    state["anonymous_id"] = uuid4().hex
    state["created_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    _write_json_file(TELEMETRY_STATE_PATH, state)
    return state


def _get_anonymous_id():
    """Return a stable anonymous telemetry identifier."""
    state = _load_telemetry_state(create=True)
    return str(state.get("anonymous_id", "")).strip()


def _track_template_usage(
    event,
    template_id,
    template_repo="",
    template_distribution="",
    template_source="",
    command="",
):
    """Best-effort usage telemetry for bundled or installed templates."""
    if _telemetry_disabled():
        return {
            "enabled": False,
            "sent": False,
            "reason": "disabled_via_env",
        }

    normalized_template_id = str(template_id or "").strip()
    if not normalized_template_id:
        return {
            "enabled": True,
            "sent": False,
            "reason": "missing_template_id",
        }

    try:
        normalized_event = _normalize_telemetry_event(event)
        normalized_distribution = _normalize_template_distribution(template_distribution)
        normalized_source = _normalize_catalog_source(template_source)
    except ValueError as exc:
        return {
            "enabled": True,
            "sent": False,
            "reason": str(exc),
        }

    payload = {
        "event": normalized_event,
        "repo": _normalize_template_repo(template_repo),
        "template_id": normalized_template_id,
        "anonymous_id": _get_anonymous_id(),
        "distribution": normalized_distribution,
        "catalog_source": normalized_source,
        "command": str(command or "").strip(),
        "client_ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }

    req = urlrequest.Request(
        f"{HUB_API_BASE}/usage",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlrequest.urlopen(req, timeout=3) as resp:
            ok = 200 <= getattr(resp, "status", 200) < 300
    except (urlerror.URLError, TimeoutError, OSError) as exc:
        return {
            "enabled": True,
            "sent": False,
            "event": normalized_event,
            "template_id": normalized_template_id,
            "error": str(exc),
        }

    result = {
        "enabled": True,
        "sent": bool(ok),
        "event": normalized_event,
        "template_id": normalized_template_id,
        "repo": payload["repo"],
    }
    if normalized_distribution:
        result["distribution"] = normalized_distribution
    if normalized_source:
        result["catalog_source"] = normalized_source
    return result


def _track_template_usage_from_args(args, event, command):
    """Track usage from optional template telemetry flags on generate/edit."""
    template_id = getattr(args, "template_id", None)
    if not template_id or getattr(args, "no_telemetry", False):
        return None

    return _track_template_usage(
        event=event,
        template_id=template_id,
        template_repo=getattr(args, "template_repo", "") or DEFAULT_TEMPLATE_REPO,
        template_distribution=getattr(args, "template_distribution", ""),
        template_source=getattr(args, "template_source", ""),
        command=command,
    )


def _resolve_profile_data(data, profile_name=None):
    """Return a config dict with the selected profile merged into top-level values."""
    return config_store.resolve_profile_data(data, profile_name=profile_name)

def _apply_json_config(config, resolved_from, data, source):
    """Merge config.json-style keys into the canonical config dict."""
    return config_store.apply_json_config(config, resolved_from, data, source, _canonicalize_model)

def _apply_env_config(config, resolved_from):
    """Merge supported environment variables into the canonical config dict."""
    return config_store.apply_env_config(config, resolved_from, _canonicalize_model)

def _apply_dotenv_values(config, resolved_from, dotenv_values, source):
    """Merge supported dotenv keys into the canonical config dict."""
    return config_store.apply_dotenv_values(config, resolved_from, dotenv_values, source, _canonicalize_model)

def _finalize_config(config, resolved_from):
    """Infer provider-related defaults after merging explicit config sources."""
    return config_store.finalize_config(config, resolved_from)

def _runtime_support_status(config):
    """Return whether the current runtime can execute the configured provider."""
    return config_store.runtime_support_status(config)

def _config_validation_errors(config):
    """Return configuration issues that block runtime execution."""
    return config_store.config_validation_errors(config)

def _resolve_default_model(config, cli_model=None):
    """Resolve the effective model with CLI args taking precedence over config."""
    return config_store.resolve_default_model(
        config,
        cli_model=cli_model,
        default_by_provider=DEFAULT_MODEL_BY_PROVIDER,
        default_model=DEFAULT_MODEL,
    )

def _load_explicit_config(path):
    """Load a user-provided config file, either JSON or .env style."""
    return config_store.load_explicit_config(path, _canonicalize_model, load_dotenv)

def _load_merged_config(config_file=None):
    """Load effective config and return config plus source metadata."""
    return config_store.load_merged_config(config_file, _canonicalize_model, load_dotenv, config_path=SKILL_CONFIG_PATH)

def _load_persisted_config_for_write():
    """Load the preferred writable BananaHub config."""
    return config_store.load_persisted_config_for_write(config_path=SKILL_CONFIG_PATH)

def _write_persisted_config(data):
    """Write BananaHub config.json with stable formatting."""
    return config_store.write_persisted_config(data, config_path=SKILL_CONFIG_PATH)

def _apply_command_provider_override(config, provider):
    """Apply a command-scoped provider override after config loading."""
    return config_store.apply_command_provider_override(config, provider)

def load_config(config_file=None):
    """Load API config with priority chain:
    1. Explicit --config file (JSON or .env)
    2. Environment variables
    3. Skill config: ~/.config/bananahub/config.json
    """
    config, _, _, _ = _load_merged_config(config_file=config_file)
    errors = _config_validation_errors(config)
    if errors:
        sources = [
            f"  --config <file>",
            f"  env GEMINI_API_KEY / GOOGLE_API_KEY",
            f"  env BANANAHUB_PROVIDER / BANANAHUB_AUTH_MODE / BANANAHUB_MODEL",
            f"  env GOOGLE_GEMINI_BASE_URL / GEMINI_BASE_URL / BANANAHUB_BASE_URL",
            f"  env GOOGLE_CLOUD_PROJECT / GOOGLE_CLOUD_LOCATION",
            f"  {SKILL_CONFIG_PATH}",
        ]
        print(json.dumps({
            "status": "error",
            "error": errors[0],
            "details": errors,
            "searched": sources,
        }, ensure_ascii=False))
        sys.exit(1)

    return config


def get_client(config):
    """Create Gemini client from config."""
    from google import genai

    runtime_support = _runtime_support_status(config)
    if not runtime_support["supported"]:
        print(json.dumps({
            "status": "error",
            "error": runtime_support["reasons"][0],
            "details": runtime_support["reasons"],
        }, ensure_ascii=False))
        sys.exit(1)

    provider = config.get("BANANAHUB_PROVIDER", DEFAULT_PROVIDER)
    api_key = config.get("OPENAI_API_KEY", "") if provider == PROVIDER_OPENAI else config.get("GEMINI_API_KEY", "")
    base_url = config.get("GOOGLE_GEMINI_BASE_URL", "")
    provider = runtime_support["provider"]
    auth_mode = runtime_support["auth_mode"]

    if auth_mode == AUTH_MODE_API_KEY and not api_key:
        print(json.dumps({"status": "error", "error": "API key not found in config"}))
        sys.exit(1)

    if provider == PROVIDER_VERTEX_AI:
        client_kwargs = {"vertexai": True}
        if auth_mode == AUTH_MODE_API_KEY:
            client_kwargs["api_key"] = api_key
        else:
            if config.get("GOOGLE_CLOUD_PROJECT"):
                client_kwargs["project"] = config.get("GOOGLE_CLOUD_PROJECT")
            if config.get("GOOGLE_CLOUD_LOCATION"):
                client_kwargs["location"] = config.get("GOOGLE_CLOUD_LOCATION")
        return genai.Client(**client_kwargs)

    endpoint_resolution = _resolve_genai_endpoint(base_url)
    http_options = {"api_version": endpoint_resolution["api_version"]}
    if base_url:
        http_options["base_url"] = endpoint_resolution["resolved_base_url"]

    return genai.Client(api_key=api_key, http_options=http_options)


def _list_config_sources(config_sources, explicit_resolved_from):
    """Return a deduped human-readable list of actual config sources."""
    return config_store.list_config_sources(config_sources, explicit_resolved_from)

def _serialize_effective_config(config):
    """Return a display-friendly config snapshot."""
    return config_store.serialize_effective_config(config, _chatgpt_base_url)

def _serialize_resolved_from(resolved_from):
    """Map internal config keys to stable public field names."""
    return config_store.serialize_resolved_from(resolved_from)

def _load_persisted_config_snapshot():
    """Return persisted config.json interpreted through the current config schema."""
    if not SKILL_CONFIG_PATH.exists():
        return None
    stored = _read_json_file(SKILL_CONFIG_PATH)
    persisted_config = {}
    persisted_resolved_from = {}
    _apply_json_config(persisted_config, persisted_resolved_from, stored, str(SKILL_CONFIG_PATH))
    _finalize_config(persisted_config, persisted_resolved_from)
    return _serialize_effective_config(persisted_config)

def _join_endpoint(base_url, path):
    """Join a configured base URL with a relative API path."""
    return provider_join_endpoint(base_url, path)

def _extract_error_message_from_payload(payload, fallback):
    """Extract a concise error message from a JSON API error payload."""
    return provider_extract_error_message_from_payload(payload, fallback)

def _http_multipart_request(method, url, headers=None, fields=None, files=None, timeout=120):
    """Send a multipart/form-data request and parse JSON response."""
    return provider_http_multipart_request(method, url, headers=headers, fields=fields, files=files, timeout=timeout)

def _http_json_request(method, url, headers=None, payload=None, timeout=60):
    """Send a JSON HTTP request and parse the JSON response."""
    return provider_http_json_request(method, url, headers=headers, payload=payload, timeout=timeout)

def _http_fetch_bytes(url, headers=None, timeout=60):
    """Fetch raw bytes from an HTTP endpoint."""
    return provider_http_fetch_bytes(url, headers=headers, timeout=timeout)

def _openai_auth_headers(config):
    """Return auth-only headers for OpenAI-compatible endpoints."""
    return openai_provider.auth_headers(config, provider_openai=PROVIDER_OPENAI, default_provider=DEFAULT_PROVIDER)

def _openai_headers(config):
    """Return auth headers for OpenAI-compatible endpoints."""
    return openai_provider.headers(config, provider_openai=PROVIDER_OPENAI, default_provider=DEFAULT_PROVIDER)

def _provider_error_hint(config, error_msg):
    """Return a provider-specific hint for common endpoint/config mistakes."""
    runtime_support = _runtime_support_status(config)
    provider = runtime_support["provider"]
    upper = str(error_msg).upper()

    if provider == PROVIDER_GEMINI_COMPATIBLE:
        if "404" in str(error_msg) or "NOT FOUND" in upper:
            return (
                "Check the gemini-compatible base_url. If the vendor docs show a `/v1beta` suffix, "
                "you can paste it directly; BananaHub now normalizes the trailing API version automatically."
            )
        if "401" in str(error_msg) or "403" in str(error_msg):
            return "Authentication failed. Check the gemini-compatible key and whether the relay expects a different auth header."

    if provider == PROVIDER_OPENAI_COMPATIBLE:
        if "404" in str(error_msg) or "NOT FOUND" in upper:
            return (
                "Check the openai-compatible base_url. Many gateways expect a `/v1` suffix. "
                "For Google's official endpoint, use `https://generativelanguage.googleapis.com/v1beta/openai`."
            )
        if "401" in str(error_msg) or "403" in str(error_msg):
            return "Authentication failed. Check the openai-compatible key and whether the endpoint expects a Bearer token."

    if provider == PROVIDER_VERTEX_AI:
        if "401" in str(error_msg) or "403" in str(error_msg):
            return "Authentication failed. Check Vertex AI auth mode, ADC readiness, or project/location permissions."
        if "404" in str(error_msg) or "NOT FOUND" in upper:
            return "Check the Vertex AI location and model availability in that project/region."

    if "401" in str(error_msg) or "403" in str(error_msg):
        return "Authentication failed. Check your provider and API key config."
    if "TIMEOUT" in upper or "CONNECT" in upper:
        return "Network error. Check your connection and provider endpoint settings."
    return ""


def _chatgpt_base_url(config):
    """Return an OpenAI-style base URL for chatgpt-compatible providers."""
    return chatgpt_provider.normalize_base_url(config, _normalize_base_url)

def _chatgpt_headers(config):
    """Return headers for chatgpt-compatible providers."""
    return chatgpt_provider.headers(config)

def _extract_image_reference_from_text(text):
    """Find a data URL, direct image URL, or markdown image reference in model text."""
    return chatgpt_provider.extract_image_reference_from_text(text)

def _extract_chatgpt_image_reference(payload):
    """Extract an image reference from chat/completions-style payloads."""
    return chatgpt_provider.extract_image_reference(payload)

def _describe_image_reference(reference):
    """Return metadata for an image reference, with full URL only behind an explicit debug flag."""
    return chatgpt_provider.describe_image_reference(reference)

def _image_bytes_from_reference(reference, headers=None, api_base_url=None):
    """Load image bytes from a data URL or HTTP URL."""
    return chatgpt_provider.image_bytes_from_reference(reference, request_headers=headers, api_base_url=api_base_url)

def _chatgpt_try_generate(config, model, prompt):
    """Generate an image through a chat/completions-style endpoint and extract returned image bytes."""
    return chatgpt_provider.try_generate(config, model, prompt, _normalize_base_url)

def _provider_base_url(config):
    """Return the OpenAI-style base URL for official or compatible providers."""
    return openai_provider.provider_base_url(config)

def _build_openai_generation_payload(
    model,
    prompt,
    aspect_ratio,
    native_image_size=None,
    openai_size=None,
    quality=None,
    background=None,
    output_format=None,
    output_compression=None,
):
    """Build an OpenAI-compatible image generation payload."""
    return openai_provider.build_generation_payload(
        model,
        prompt,
        aspect_ratio,
        native_image_size=native_image_size,
        openai_size=openai_size,
        quality=quality,
        background=background,
        output_format=output_format,
        output_compression=output_compression,
    )

def _list_openai_models(config):
    """List models from an OpenAI-compatible endpoint."""
    return openai_provider.list_models(
        config,
        resolve_endpoint=_resolve_openai_endpoint,
        canonicalize_model=_canonicalize_model,
        default_model=DEFAULT_MODEL,
        provider_openai=PROVIDER_OPENAI,
        default_provider=DEFAULT_PROVIDER,
    )

def _openai_try_generate(config, model, prompt, aspect_ratio, image_size=None, openai_size=None, quality=None, background=None, output_format=None, output_compression=None):
    """Attempt image generation against an OpenAI-compatible endpoint."""
    return openai_provider.try_generate(
        config,
        model,
        prompt,
        aspect_ratio,
        resolve_endpoint=_resolve_openai_endpoint,
        image_size=image_size,
        openai_size=openai_size,
        quality=quality,
        background=background,
        output_format=output_format,
        output_compression=output_compression,
        provider_openai=PROVIDER_OPENAI,
        default_provider=DEFAULT_PROVIDER,
    )

def _extract_openai_image_bytes(response):
    """Extract image bytes from OpenAI Images API response."""
    return openai_provider.extract_image_bytes(response)

def _openai_try_edit(config, model, prompt, input_path, ref_paths=None, mask_path=None, size=None):
    """Attempt OpenAI-native image editing via multipart Images API."""
    return openai_provider.try_edit(
        config,
        model,
        prompt,
        input_path,
        resolve_endpoint=_resolve_openai_endpoint,
        ref_paths=ref_paths,
        mask_path=mask_path,
        size=size,
        provider_openai=PROVIDER_OPENAI,
        default_provider=DEFAULT_PROVIDER,
    )

def _provider_healthcheck(config):
    """Run a low-cost provider-aware healthcheck."""
    runtime_support = _runtime_support_status(config)
    if not runtime_support["supported"]:
        raise RuntimeError(runtime_support["reasons"][0])

    if runtime_support["transport"] == TRANSPORT_OPENAI_REST:
        models = _list_openai_models(config)
        return {
            "mode": "models.list",
            "response": f"{len(models)} model(s) visible",
        }

    client = get_client(config)
    response = client.models.generate_content(
        model=_resolve_default_model(config),
        contents="Say OK",
    )
    text = ""
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                text = part.text
                break
    return {
        "mode": "generate_content",
        "response": text[:100],
    }


def cmd_init(args):
    """Check environment readiness and guide user through setup."""
    checks = []

    # 1. Check config sources
    config, resolved_from, config_sources, explicit_resolved_from = _load_merged_config(
        config_file=getattr(args, "config", None)
    )
    actual_sources = _list_config_sources(config_sources, explicit_resolved_from)

    if actual_sources:
        checks.append({
            "name": "config_source",
            "ok": True,
            "sources": actual_sources,
            "preferred_path": str(SKILL_CONFIG_PATH),
        })
    else:
        checks.append({
            "name": "config_source",
            "ok": False,
            "error": f"No config found. Create {SKILL_CONFIG_PATH} or use environment variables.",
        })

    # 2. Check provider resolution and runtime support
    runtime_support = _runtime_support_status(config)
    checks.append({
        "name": "provider",
        "ok": True,
        "value": config.get("BANANAHUB_PROVIDER"),
        "transport": runtime_support["transport"],
        "auth_mode": runtime_support["auth_mode"],
        "source": resolved_from.get("BANANAHUB_PROVIDER"),
    })
    checks.append({
        "name": "runtime_support",
        "ok": runtime_support["supported"],
        "provider": runtime_support["provider"],
        "transport": runtime_support["transport"],
        "auth_mode": runtime_support["auth_mode"],
        "capabilities": runtime_support["capabilities"],
        "detail": runtime_support["reasons"] or ["ready"],
    })

    # 3. Check API key
    api_key, api_key_name, api_key_type = _active_api_key(config, runtime_support)
    if runtime_support["auth_mode"] != AUTH_MODE_API_KEY:
        checks.append({
            "name": "api_key",
            "ok": True,
            "value": "(not required for current auth_mode)",
            "source": resolved_from.get(api_key_name) if api_key_name else None,
        })
    elif api_key:
        checks.append({
            "name": "api_key",
            "ok": True,
            "value": _mask_secret(api_key),
            "config_key": api_key_name,
            "type": api_key_type,
            "source": resolved_from.get(api_key_name),
        })
    else:
        checks.append({
            "name": "api_key",
            "ok": False,
            "config_key": api_key_name,
            "type": api_key_type,
            "error": "API key not found in any config source for the selected provider.",
        })

    # 4. Check endpoint / base URL
    if runtime_support["provider"] == PROVIDER_CHATGPT_COMPATIBLE:
        base_url = config.get("BANANAHUB_CHATGPT_BASE_URL", "")
        base_url_source = resolved_from.get("BANANAHUB_CHATGPT_BASE_URL")
    elif runtime_support["provider"] == PROVIDER_OPENAI:
        base_url = config.get("OPENAI_BASE_URL", "")
        base_url_source = resolved_from.get("OPENAI_BASE_URL")
    elif runtime_support["transport"] == TRANSPORT_OPENAI_REST:
        base_url = config.get("OPENAI_BASE_URL") or config.get("GOOGLE_GEMINI_BASE_URL", "")
        base_url_source = resolved_from.get("OPENAI_BASE_URL") or resolved_from.get("GOOGLE_GEMINI_BASE_URL")
    else:
        base_url = config.get("GOOGLE_GEMINI_BASE_URL", "")
        base_url_source = resolved_from.get("GOOGLE_GEMINI_BASE_URL")

    if runtime_support["provider"] == PROVIDER_GEMINI_COMPATIBLE and not base_url:
        checks.append({
            "name": "base_url",
            "ok": False,
            "error": "provider 'gemini-compatible' requires a base_url.",
        })
    elif runtime_support["provider"] == PROVIDER_OPENAI_COMPATIBLE and not base_url:
        checks.append({
            "name": "base_url",
            "ok": False,
            "error": "provider 'openai-compatible' requires a base_url.",
        })
    elif runtime_support["provider"] == PROVIDER_CHATGPT_COMPATIBLE and not base_url:
        checks.append({
            "name": "base_url",
            "ok": False,
            "error": "provider 'chatgpt-compatible' requires a chatgpt_base_url.",
        })
    elif base_url:
        endpoint_resolution = (
            _resolve_openai_endpoint(base_url)
            if runtime_support["transport"] == TRANSPORT_OPENAI_REST
            else _resolve_genai_endpoint(base_url)
        )
        checks.append({
            "name": "base_url",
            "ok": True,
            "value": base_url,
            "source": base_url_source,
            "mode": "custom_endpoint" if runtime_support["provider"] != PROVIDER_GOOGLE_AI_STUDIO else "override_endpoint",
            "resolved_base_url": endpoint_resolution.get("resolved_base_url"),
            "api_version": endpoint_resolution.get("api_version"),
            "warnings": endpoint_resolution.get("warnings"),
        })
    else:
        checks.append({"name": "base_url", "ok": True, "value": "(provider default endpoint)", "mode": "provider_default"})

    # 5. Show configured default model when present
    model = config.get("BANANAHUB_MODEL", "")
    checks.append({
        "name": "default_model",
        "ok": True,
        "value": model or DEFAULT_MODEL,
        "source": resolved_from.get("BANANAHUB_MODEL") if model else f"default:{DEFAULT_MODEL}",
    })

    # 6. Check Python dependencies
    deps = {}
    for pkg, import_name in [("google-genai", "google.genai"), ("pillow", "PIL")]:
        try:
            __import__(import_name)
            deps[pkg] = True
        except ImportError:
            deps[pkg] = False
    checks.append({"name": "dependencies", "ok": all(deps.values()), "detail": deps})

    all_ok = all(c["ok"] for c in checks)

    # 7. API connectivity test (only if basic checks pass)
    if all_ok and not args.skip_test:
        try:
            healthcheck = _provider_healthcheck(config)
            checks.append({"name": "api_test", "ok": True, **healthcheck})
        except Exception as e:
            checks.append({"name": "api_test", "ok": False, "error": str(e)[:200]})

    all_ok = all(c["ok"] for c in checks)

    setup_guide = None
    if not all_ok:
        setup_guide = {
            "steps": [
                "Option A (recommended): Google AI Studio / Gemini Developer API:",
                "  1. Create or manage a key in Google AI Studio: https://aistudio.google.com/apikey",
                "  2. python3 bananahub.py config set --provider google-ai-studio --api-key <your_api_key>",
                "  3. Optional default model: python3 bananahub.py config set --model gemini-3.1-flash-image-preview",
                f"  4. Review effective config: python3 bananahub.py config show",
                "Option B: Gemini-compatible relay / proxy:",
                "  1. python3 bananahub.py config set --provider gemini-compatible --base-url https://your-gemini-compatible-endpoint --api-key <your_proxy_key>",
                "  2. Optional default model: python3 bananahub.py config set --model gemini-2.5-flash-image",
                f"  3. Review effective config: python3 bananahub.py config show",
                "Option C: OpenAI-compatible endpoint:",
                "  1. python3 bananahub.py config set --provider openai-compatible --base-url https://your-openai-compatible-endpoint --api-key <your_api_key>",
                "  2. Optional default model: python3 bananahub.py config set --model gemini-2.0-flash-preview-image-generation",
                f"  3. Review effective config: python3 bananahub.py config show",
                "Option D: Vertex AI:",
                "  1. ADC mode: python3 bananahub.py config set --provider vertex-ai --auth-mode adc --project <gcp-project> --location global",
                "  2. Express mode key: python3 bananahub.py config set --provider vertex-ai --auth-mode api_key --api-key <vertex_api_key>",
                f"  3. Review effective config: python3 bananahub.py config show",
                "Option E: Create BananaHub config manually:",
                f"  1. mkdir -p {SKILL_CONFIG_DIR}",
                f'  2. Create {SKILL_CONFIG_PATH} with:',
                '     {"provider": "google-ai-studio", "api_key": "your_api_key_here", "model": "gemini-3-pro-image-preview"}',
                "     or",
                '     {"provider": "gemini-compatible", "api_key": "your_proxy_key_here", "base_url": "https://your-endpoint"}',
                "     or",
                '     {"provider": "openai-compatible", "api_key": "your_api_key_here", "base_url": "https://your-openai-endpoint"}',
                "     or",
                '     {"provider": "vertex-ai", "auth_mode": "adc", "project": "your-gcp-project", "location": "global"}',
                "Option F: Use environment variables:",
                "  export GOOGLE_API_KEY=your_api_key_here  # or GEMINI_API_KEY",
                "  export BANANAHUB_PROVIDER=google-ai-studio",
                "  export BANANAHUB_MODEL=gemini-3-pro-image-preview  # optional",
                "  export BANANAHUB_PROVIDER=gemini-compatible        # for relay/proxy users",
                "  export GOOGLE_GEMINI_BASE_URL=https://your-gemini-compatible-endpoint",
                "  export BANANAHUB_PROVIDER=openai-compatible       # for OpenAI-style endpoints",
                "  export BANANAHUB_PROVIDER=vertex-ai",
                "  export BANANAHUB_AUTH_MODE=adc                     # or api_key",
                "  export GOOGLE_CLOUD_PROJECT=your-gcp-project       # Vertex AI",
                "  export GOOGLE_CLOUD_LOCATION=global                # Vertex AI",
                "",
                "OpenAI-native provider supports generate/edit/mask-edit through OpenAI image endpoints.",
                "OpenAI-compatible endpoint capabilities are vendor-dependent; do not assume edit or mask-edit support.",
                "Google pricing and quota policy may apply depending on model/account/region.",
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


def cmd_config_show(args):
    """Show effective and persisted config state."""
    config, resolved_from, config_sources, explicit_resolved_from = _load_merged_config(
        config_file=getattr(args, "config", None)
    )
    runtime_support = _runtime_support_status(config)

    response = {
        "status": "ok",
        "preferred_path": str(SKILL_CONFIG_PATH),
        "existing_sources": _list_config_sources(config_sources, explicit_resolved_from),
        "effective_config": _serialize_effective_config(config),
        "resolved_from": _serialize_resolved_from(resolved_from),
        "runtime_support": runtime_support,
        "custom_endpoint_enabled": bool(config.get("GOOGLE_GEMINI_BASE_URL") or config.get("OPENAI_BASE_URL") or config.get("BANANAHUB_CHATGPT_BASE_URL")),
        "telemetry": {
            "enabled": not _telemetry_disabled(),
            "endpoint": f"{HUB_API_BASE}/usage",
            "state_file": str(TELEMETRY_STATE_PATH),
            "anonymous_id": _load_telemetry_state(create=not _telemetry_disabled()).get("anonymous_id")
            if not _telemetry_disabled()
            else None,
        },
    }

    response["persisted_config"] = _load_persisted_config_snapshot()

    print(json.dumps(response, ensure_ascii=False, indent=2))


def cmd_config_set(args):
    """Persist BananaHub config under ~/.config/bananahub/config.json."""
    if (
        not args.api_key
        and not args.profile
        and not args.default_profile
        and not args.provider
        and not args.auth_mode
        and not args.model
        and args.project is None
        and args.location is None
        and args.base_url is None
        and not args.clear_base_url
        and not args.clear_model
        and not args.clear_project
        and not args.clear_location
    ):
        print(json.dumps({
            "status": "error",
            "error": "Nothing to update. Use --profile, --default-profile, --api-key, --provider, --auth-mode, --project, --location, --model, --base-url, or the clear-* flags.",
        }, ensure_ascii=False))
        sys.exit(1)

    try:
        persisted_config = _load_persisted_config_for_write()
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)

    target_config = persisted_config
    if args.profile:
        profiles = persisted_config.setdefault("profiles", {})
        target_config = profiles.setdefault(args.profile, {})

    if args.default_profile:
        persisted_config["default_profile"] = args.default_profile.strip()

    explicit_provider = None
    normalized_provider_for_key = None
    if args.provider:
        try:
            normalized_provider_for_key = _normalize_provider(args.provider)
        except ValueError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
            sys.exit(1)

    if args.api_key:
        if normalized_provider_for_key == PROVIDER_OPENAI:
            key_name = "openai_api_key"
        elif normalized_provider_for_key == PROVIDER_CHATGPT_COMPATIBLE:
            key_name = "chatgpt_api_key"
        else:
            key_name = "api_key"
        target_config[key_name] = args.api_key.strip()

    if args.provider:
        explicit_provider = normalized_provider_for_key
        target_config["provider"] = explicit_provider

    if args.auth_mode:
        try:
            target_config["auth_mode"] = _normalize_auth_mode(args.auth_mode)
        except ValueError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
            sys.exit(1)

    if args.clear_model:
        target_config.pop("model", None)
    elif args.model is not None:
        normalized_model = _normalize_model(args.model)
        if normalized_model:
            target_config["model"] = normalized_model
        else:
            target_config.pop("model", None)

    if args.clear_project:
        target_config.pop("project", None)
    elif args.project is not None:
        normalized_project = str(args.project).strip()
        if normalized_project:
            target_config["project"] = normalized_project
        else:
            target_config.pop("project", None)

    if args.clear_location:
        target_config.pop("location", None)
    elif args.location is not None:
        normalized_location = str(args.location).strip()
        if normalized_location:
            target_config["location"] = normalized_location
        else:
            target_config.pop("location", None)

    if args.clear_base_url:
        target_config.pop("base_url", None)
        target_config.pop("openai_base_url", None)
        target_config.pop("chatgpt_base_url", None)
    elif args.base_url is not None:
        try:
            normalized_base_url = _normalize_base_url(args.base_url)
        except ValueError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
            sys.exit(1)
        if normalized_base_url:
            if explicit_provider == PROVIDER_CHATGPT_COMPATIBLE or target_config.get("provider") == PROVIDER_CHATGPT_COMPATIBLE:
                target_config["chatgpt_base_url"] = normalized_base_url
            elif explicit_provider == PROVIDER_OPENAI or target_config.get("provider") == PROVIDER_OPENAI:
                target_config["openai_base_url"] = normalized_base_url
            else:
                target_config["base_url"] = normalized_base_url
        else:
            target_config.pop("base_url", None)
            target_config.pop("openai_base_url", None)
            target_config.pop("chatgpt_base_url", None)

    if "provider" not in target_config:
        target_config["provider"] = (
            PROVIDER_GEMINI_COMPATIBLE if target_config.get("base_url") else PROVIDER_GOOGLE_AI_STUDIO
        )

    if args.base_url is not None and not explicit_provider and target_config.get("base_url"):
        target_config["provider"] = PROVIDER_GEMINI_COMPATIBLE

    if args.clear_base_url and not explicit_provider and target_config.get("provider") == PROVIDER_GEMINI_COMPATIBLE:
        target_config["provider"] = PROVIDER_GOOGLE_AI_STUDIO

    if target_config.get("provider") == PROVIDER_GEMINI_COMPATIBLE and not target_config.get("base_url"):
        print(json.dumps({
            "status": "error",
            "error": "provider 'gemini-compatible' requires a base_url. Use --base-url or switch --provider google-ai-studio.",
        }, ensure_ascii=False))
        sys.exit(1)

    if target_config.get("provider") == PROVIDER_OPENAI_COMPATIBLE and not (target_config.get("base_url") or target_config.get("openai_base_url")):
        print(json.dumps({
            "status": "error",
            "error": "provider 'openai-compatible' requires a base_url. Use --base-url to point at an OpenAI-compatible endpoint.",
        }, ensure_ascii=False))
        sys.exit(1)

    if target_config.get("provider") == PROVIDER_CHATGPT_COMPATIBLE and not target_config.get("chatgpt_base_url"):
        print(json.dumps({
            "status": "error",
            "error": "provider 'chatgpt-compatible' requires --base-url or chatgpt_base_url.",
        }, ensure_ascii=False))
        sys.exit(1)

    if target_config.get("provider") == PROVIDER_GOOGLE_AI_STUDIO and target_config.get("base_url"):
        print(json.dumps({
            "status": "error",
            "error": "provider 'google-ai-studio' cannot keep a custom base_url. Use --clear-base-url or switch --provider gemini-compatible.",
        }, ensure_ascii=False))
        sys.exit(1)

    if target_config.get("provider") == PROVIDER_VERTEX_AI and target_config.get("base_url"):
        print(json.dumps({
            "status": "error",
            "error": "provider 'vertex-ai' does not use base_url in this runtime. Clear it or switch provider.",
        }, ensure_ascii=False))
        sys.exit(1)

    try:
        _write_persisted_config(persisted_config)
    except OSError as exc:
        print(json.dumps({"status": "error", "error": f"Failed to write config: {exc}"}))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "file": str(SKILL_CONFIG_PATH),
        "config": _load_persisted_config_snapshot(),
    }, ensure_ascii=False, indent=2))


def cmd_telemetry_status(args):
    """Show local telemetry identity and endpoint state."""
    state = _load_telemetry_state(create=not _telemetry_disabled())
    anonymous_id = str(state.get("anonymous_id", "")).strip()

    print(json.dumps({
        "status": "ok",
        "enabled": not _telemetry_disabled(),
        "endpoint": f"{HUB_API_BASE}/usage",
        "state_file": str(TELEMETRY_STATE_PATH),
        "anonymous_id": anonymous_id or None,
    }, ensure_ascii=False, indent=2))


def cmd_telemetry_track(args):
    """Send an explicit template usage telemetry event."""
    try:
        result = _track_template_usage(
            event=args.event,
            template_id=args.template_id,
            template_repo=args.template_repo,
            template_distribution=args.template_distribution,
            template_source=args.template_source,
            command=args.command_name,
        )
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)

    payload = {
        "status": "ok" if result.get("sent") or not result.get("enabled", True) else "skipped",
        "telemetry": result,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_check_mode(args):
    """Report the executable BananaHub mode and capability layer boundaries."""
    config, resolved_from, config_sources, explicit_resolved_from = _load_merged_config(
        config_file=getattr(args, "config", None)
    )
    config = _apply_command_provider_override(config, getattr(args, "provider", None))
    runtime_support = _runtime_support_status(config)
    validation_errors = _config_validation_errors(config)
    active_key, active_key_name, active_key_type = _active_api_key(config, runtime_support)
    host_native_available = _host_imagegen_available(args)
    provider_ready = runtime_support["supported"] and not validation_errors

    if provider_ready:
        mode = "provider-backed"
        recommendation = "run-generate-or-edit"
        summary = "Provider-backed mode: BananaHub can call the configured image provider and save outputs."
    elif host_native_available:
        mode = "host-native"
        recommendation = "delegate-to-host-image-tool"
        summary = "Host-native mode: BananaHub should optimize/render the prompt, then hand it to the host image tool."
    else:
        mode = "prompt-only"
        recommendation = "archive-and-return-prompt"
        summary = "Prompt-only advisor mode: BananaHub can still optimize, template, and archive prompts, but cannot call an image provider."

    response = {
        "status": "ok",
        "mode": mode,
        "recommendation": recommendation,
        "summary": summary,
        "provider_ready": provider_ready,
        "host_native_available": host_native_available,
        "existing_sources": _list_config_sources(config_sources, explicit_resolved_from),
        "effective_config": _serialize_effective_config(config),
        "resolved_from": _serialize_resolved_from(resolved_from),
        "runtime_support": runtime_support,
        "validation_errors": validation_errors,
        "active_api_key": {
            "required": runtime_support["auth_mode"] == AUTH_MODE_API_KEY,
            "present": bool(active_key),
            "config_key": active_key_name,
            "type": active_key_type,
            "source": resolved_from.get(active_key_name) if active_key_name else None,
        },
        "capability_layers": {
            "skill_workflow_cross_model": [
                "prompt_optimization",
                "translation_policy",
                "conservative_enhancement",
                "prompt_archiving",
                "template_discovery",
                "template_activation",
                "host_native_delegation",
                "prompt_only_advisor",
            ],
            "provider_or_model_scoped": [
                "image_edit",
                "mask_edit",
                "multi_reference",
                "transparent_background",
                "custom_size",
                "native_quality",
                "output_format",
                "model_fallback",
            ],
        },
        "prompt_archive": {
            "default_dir": DEFAULT_PROMPT_ARCHIVE_DIR,
            "enabled_by_env": _is_truthy(os.environ.get("BANANAHUB_SAVE_PROMPTS", "")),
            "flags": ["--save-prompt", "--prompt-output <path>"],
        },
    }

    print(json.dumps(response, ensure_ascii=False, indent=2 if getattr(args, "pretty", False) else None))


IMAGE_KEYWORDS = {"image", "imagen"}
DEFAULT_MODEL = "gemini-3-pro-image-preview"
DEFAULT_MODEL_BY_PROVIDER = {
    PROVIDER_GOOGLE_AI_STUDIO: "gemini-3-pro-image-preview",
    PROVIDER_GEMINI_COMPATIBLE: "gemini-3-pro-image-preview",
    PROVIDER_VERTEX_AI: "gemini-3-pro-image-preview",
    PROVIDER_OPENAI: "gpt-image-2",
    PROVIDER_OPENAI_COMPATIBLE: "gpt-image-2",
    PROVIDER_CHATGPT_COMPATIBLE: "gpt-5.4",
}
MODEL_ALIASES = {
    "nano-banana": "gemini-2.5-flash-image",
    "nano-banana-1": "gemini-2.5-flash-image",
    "nano-banana-pro": "gemini-3-pro-image-preview",
    "nano-banana-pro-preview": "gemini-3-pro-image-preview",
    "nano-banana-2": "gemini-3.1-flash-image-preview",
    "gpt-image2": "gpt-image-2",
    "gpt image 2": "gpt-image-2",
    "gpt-image15": "gpt-image-1.5",
    "gpt image 1.5": "gpt-image-1.5",
    "gpt image": "gpt-image-1",
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
OPENAI_MODEL_FALLBACK_CHAIN = [
    "gpt-image-2",
    "gpt-image-1.5",
    "gpt-image-1",
]

# HTTP status codes that trigger fallback (server-side, not user's fault)
FALLBACK_STATUS_CODES = {"500", "502", "503", "504", "UNAVAILABLE", "INTERNAL", "OVERLOADED"}
TRANSIENT_NETWORK_ERROR_MARKERS = {
    "REMOTE END CLOSED CONNECTION WITHOUT RESPONSE",
    "REMOTEDISCONNECTED",
    "CONNECTION RESET",
    "CONNECTIONRESETERROR",
    "CONNECTION ABORTED",
    "CONNECTIONABORTEDERROR",
    "CONNECTION REFUSED",
    "BROKEN PIPE",
    "TIMED OUT",
    "TIMEOUT",
    "TEMPORARILY UNAVAILABLE",
}
NON_RETRYABLE_ERROR_MARKERS = {
    "HTTP 400",
    "HTTP 401",
    "HTTP 403",
    "UNAUTHORIZED",
    "FORBIDDEN",
    "AUTHENTICATION",
    "INVALID API KEY",
    "INVALID_API_KEY",
    "PERMISSION DENIED",
    "CONTENT POLICY",
    "POLICY VIOLATION",
    "SAFETY",
    "BLOCKED",
    "MODERATION",
}

FALLBACK_MODELS = [
    {"id": "gemini-3-pro-image-preview", "display_name": "Gemini 3 Pro Image Preview", "default": True},
    {"id": "gemini-3.1-flash-image-preview", "display_name": "Gemini 3.1 Flash Image Preview", "default": False},
    {"id": "gemini-2.5-flash-image", "display_name": "Gemini 2.5 Flash Image", "default": False},
    {"id": "gemini-2.0-flash-preview-image-generation", "display_name": "Gemini 2.0 Flash Image Generation", "default": False},
]
OPENAI_FALLBACK_MODELS = [
    {"id": "gpt-image-2", "display_name": "GPT Image 2", "default": True},
    {"id": "gpt-image-1.5", "display_name": "GPT Image 1.5", "default": False},
    {"id": "gpt-image-1", "display_name": "GPT Image 1", "default": False},
]
CHATGPT_FALLBACK_MODELS = [
    {"id": "gpt-5.4", "display_name": "GPT 5.4 Chat Image", "default": True},
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


def _add_template_telemetry_flags(parser):
    """Attach optional template telemetry metadata to generate/edit commands."""
    parser.add_argument("--template-id", help="Template id for success telemetry")
    parser.add_argument("--template-repo", help=f"Template repo for telemetry (default: {DEFAULT_TEMPLATE_REPO})")
    parser.add_argument(
        "--template-distribution",
        choices=sorted(VALID_TEMPLATE_DISTRIBUTIONS),
        help="Template distribution for telemetry (bundled or remote)",
    )
    parser.add_argument(
        "--template-source",
        choices=sorted(VALID_CATALOG_SOURCES),
        help="Template source layer for telemetry (curated or discovered)",
    )
    parser.add_argument("--no-telemetry", action="store_true", help="Disable best-effort template telemetry for this run")


def _is_server_error(exception):
    """Check if an exception is a transient server/network error eligible for retry or fallback."""
    msg = str(exception).upper()
    if any(marker in msg for marker in NON_RETRYABLE_ERROR_MARKERS):
        return False
    return any(code in msg for code in FALLBACK_STATUS_CODES) or any(
        marker in msg for marker in TRANSIENT_NETWORK_ERROR_MARKERS
    )


def _fallback_chain_for_provider(provider):
    """Return the provider-family fallback chain without crossing providers."""
    if provider in {PROVIDER_OPENAI, PROVIDER_OPENAI_COMPATIBLE}:
        return OPENAI_MODEL_FALLBACK_CHAIN
    if provider == PROVIDER_CHATGPT_COMPATIBLE:
        return ["gpt-5.4"]
        return OPENAI_MODEL_FALLBACK_CHAIN
    return MODEL_FALLBACK_CHAIN


def _get_fallback_models(current_model, provider=None):
    """Return fallback models to try after current_model fails within one provider family."""
    current_model = _canonicalize_model(current_model)
    chain = _fallback_chain_for_provider(provider or DEFAULT_PROVIDER)
    if current_model in chain:
        idx = chain.index(current_model)
        return chain[idx + 1:]
    return [m for m in chain if m != current_model]


def _fallback_models_for_provider(provider):
    if provider == PROVIDER_CHATGPT_COMPATIBLE:
        return CHATGPT_FALLBACK_MODELS
    if provider in {PROVIDER_OPENAI, PROVIDER_OPENAI_COMPATIBLE}:
        return OPENAI_FALLBACK_MODELS
    return FALLBACK_MODELS


def cmd_models(args):
    """List available image generation models from the API, with fallback."""
    config = _apply_command_provider_override(load_config(getattr(args, "config", None)), getattr(args, "provider", None))
    runtime_support = _runtime_support_status(config)
    provider_fallback_models = _fallback_models_for_provider(runtime_support["provider"])
    try:
        if runtime_support["provider"] == PROVIDER_CHATGPT_COMPATIBLE:
            print(json.dumps({"status": "ok", "source": "static", "models": provider_fallback_models}, ensure_ascii=False))
            return

        if runtime_support["transport"] == TRANSPORT_OPENAI_REST:
            models = _list_openai_models(config)
            filtered = [m for m in models if any(kw in m["id"].lower() for kw in IMAGE_KEYWORDS)]
            if filtered:
                models = filtered
            elif not models:
                models = provider_fallback_models
                print(json.dumps({"status": "ok", "source": "fallback", "models": models}, ensure_ascii=False))
                return

            models = sorted(models, key=lambda x: (not x["default"], x["id"]))
            print(json.dumps({"status": "ok", "source": "api", "models": models}, ensure_ascii=False))
            return

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
        print(json.dumps({"status": "ok", "source": "fallback", "models": provider_fallback_models}, ensure_ascii=False))

    except Exception as e:
        # API call failed — use fallback
        print(json.dumps({
            "status": "ok",
            "source": "fallback",
            "warning": f"API query failed: {str(e)[:150]}",
            "models": provider_fallback_models,
        }, ensure_ascii=False))


def _try_edit(client, model, prompt, input_images, image_size=None):
    """Attempt image editing with a single model."""
    from google.genai import types

    return gemini_provider.try_edit(client, types, model, prompt, input_images, image_size=image_size)

def _default_output_path(prefix, model):
    """Build the default output path for generated assets."""
    output_dir = Path.cwd()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_short = model.replace("gemini-", "").replace("-preview", "").replace("-image-generation", "")
    return output_dir / f"{prefix}_{model_short}_{timestamp}.png"


def _slugify_prompt(value, fallback="prompt"):
    """Create a short ASCII slug for prompt archive files."""
    base = str(value or "").strip().lower()
    base = re.sub(r"[^a-z0-9]+", "-", base)
    base = base.strip("-")[:48]
    return base or fallback


def _default_prompt_archive_path(command, prompt):
    """Build the default prompt archive path under the current working directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slugify_prompt(" ".join(str(prompt).split()[:8]))
    return Path.cwd() / DEFAULT_PROMPT_ARCHIVE_DIR / f"{command}_{slug}_{timestamp}.md"


def _resolve_prompt_archive_path(prompt, command="prompt", prompt_output=None):
    """Resolve a prompt archive path from an explicit path or the default archive directory."""
    if prompt_output:
        target = Path(prompt_output)
        if target.suffix:
            return target
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = _slugify_prompt(" ".join(str(prompt).split()[:8]))
        return target / f"{command}_{slug}_{timestamp}.md"
    return _default_prompt_archive_path(command, prompt)


def _prompt_archive_requested(args):
    """Return whether this command should save the final prompt."""
    return bool(
        getattr(args, "prompt_output", None)
        or getattr(args, "save_prompt", False)
        or _is_truthy(os.environ.get("BANANAHUB_SAVE_PROMPTS", ""))
    )


def _write_prompt_archive(prompt, command="prompt", prompt_output=None, metadata=None):
    """Persist a final prompt as Markdown and return the saved path."""
    path = _resolve_prompt_archive_path(prompt, command=command, prompt_output=prompt_output)
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "command": command,
    }
    if metadata:
        for key, value in metadata.items():
            if value not in (None, "", [], {}):
                frontmatter[key] = value
    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, (list, dict)):
            rendered = json.dumps(value, ensure_ascii=False)
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    lines.extend(["---", "", str(prompt).strip(), ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _archive_prompt_for_command(args, prompt, command, metadata=None):
    """Save a prompt for generate/edit when requested by CLI flag or environment."""
    if not _prompt_archive_requested(args):
        return None
    return _write_prompt_archive(
        prompt,
        command=command,
        prompt_output=getattr(args, "prompt_output", None),
        metadata=metadata,
    )


def _save_png_bytes(image_bytes, output_path, resize_dims=None):
    """Persist image bytes as PNG, optionally resizing first."""
    from PIL import Image
    import io

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(io.BytesIO(image_bytes))
    if resize_dims:
        image = image.resize(resize_dims, Image.LANCZOS)
    image.save(str(output_path), "PNG")
    return image


def cmd_edit(args):
    """Edit an existing image based on a text prompt, with automatic model fallback."""
    import io

    try:
        native_image_size, resize_dims, option_warnings = _resolve_image_request_options(args)
    except ValueError as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    config_data = _apply_command_provider_override(load_config(getattr(args, "config", None)), getattr(args, "provider", None))
    runtime_support = _runtime_support_status(config_data)
    if getattr(args, "dry_run", False):
        requested_model_input = _resolve_default_model(config_data, args.model)
        requested_model = _canonicalize_model(requested_model_input)
        prompt_archive = None
        if _prompt_archive_requested(args):
            prompt_archive = str(_resolve_prompt_archive_path(args.prompt, command="edit", prompt_output=getattr(args, "prompt_output", None)))
        print(json.dumps({
            "status": "ok",
            "dry_run": True,
            "command": "edit",
            "provider": runtime_support["provider"],
            "transport": runtime_support["transport"],
            "capabilities": runtime_support["capabilities"],
            "requested_model": requested_model_input,
            "resolved_model": requested_model,
            "prompt": args.prompt,
            "input": args.input,
            "ref": args.ref or [],
            "mask": getattr(args, "mask", None),
            "prompt_archive": prompt_archive,
            "native_image_size": native_image_size,
            "post_resize": f"{resize_dims[0]}x{resize_dims[1]}" if resize_dims else None,
            "provider_options": {
                "openai_size": getattr(args, "openai_size", None),
                "quality": getattr(args, "quality", None),
                "background": getattr(args, "background", None),
                "output_format": getattr(args, "output_format", None),
                "output_compression": getattr(args, "output_compression", None),
            },
            "warnings": option_warnings,
        }, ensure_ascii=False))
        return

    if not runtime_support["capabilities"].get("edit", False):
        print(json.dumps({
            "status": "error",
            "error": (
                f"provider '{runtime_support['provider']}' does not support image edit in this runtime yet. "
                "Use google-ai-studio, gemini-compatible, vertex-ai, or openai for edit."
            ),
        }, ensure_ascii=False))
        sys.exit(1)

    # Validate input image before importing heavy dependencies
    input_path = Path(args.input)
    if not input_path.exists():
        print(json.dumps({
            "status": "error",
            "error": f"Input image not found: {input_path}",
        }, ensure_ascii=False))
        sys.exit(1)

    mask_path = None
    if getattr(args, "mask", None):
        mask_path = Path(args.mask)
        if not mask_path.exists():
            print(json.dumps({
                "status": "error",
                "error": f"Mask image not found: {mask_path}",
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

    max_refs = 13
    if runtime_support["provider"] == PROVIDER_OPENAI:
        max_refs = 9
    if len(ref_paths) > max_refs:
        print(json.dumps({
            "status": "error",
            "error": f"Too many reference images: {len(ref_paths)}. Maximum is {max_refs} reference images for provider {runtime_support['provider']}.",
        }, ensure_ascii=False))
        sys.exit(1)

    if runtime_support["provider"] != PROVIDER_OPENAI and mask_path:
        print(json.dumps({
            "status": "error",
            "error": "--mask is only supported by the OpenAI-native provider in this runtime.",
        }, ensure_ascii=False))
        sys.exit(1)

    if 1 + len(ref_paths) > 14 and runtime_support["provider"] != PROVIDER_OPENAI:
        print(json.dumps({
            "status": "error",
            "error": f"Too many input images: {1 + len(ref_paths)}. Total images (input + refs) must be 14 or fewer.",
        }, ensure_ascii=False))
        sys.exit(1)

    requested_model_input = _resolve_default_model(config_data, args.model)
    requested_model = _canonicalize_model(requested_model_input)
    prompt = args.prompt
    no_fallback = getattr(args, "no_fallback", False)
    retries = getattr(args, "retries", 1)
    user_output = args.output
    saved_prompt_path = _archive_prompt_for_command(
        args,
        prompt,
        "edit",
        metadata={
            "provider": runtime_support["provider"],
            "requested_model": requested_model_input,
            "input": str(input_path),
            "ref": [str(rp) for rp in ref_paths],
            "mask": str(mask_path) if mask_path else None,
        },
    )

    if no_fallback:
        models_to_try = [requested_model]
    else:
        models_to_try = _dedupe_preserve_order([requested_model] + _get_fallback_models(requested_model, runtime_support["provider"]))

    if runtime_support["transport"] == TRANSPORT_OPENAI_REST:
        tried = []
        last_error = None
        for model in models_to_try:
            for attempt in range(1 + retries):
                try:
                    image_bytes, extra_warnings, gen_error = _openai_try_edit(
                        config_data,
                        model,
                        prompt,
                        input_path,
                        ref_paths=ref_paths,
                        mask_path=mask_path,
                    )
                    if gen_error:
                        print(json.dumps({
                            "status": "error",
                            "error": gen_error,
                            "prompt": prompt,
                            "prompt_file": str(saved_prompt_path) if saved_prompt_path else None,
                            "requested_model": requested_model_input,
                            "actual_model": model,
                        }, ensure_ascii=False))
                        sys.exit(1)

                    output_path = Path(user_output) if user_output else _default_output_path("bananahub_edit", model)
                    image = _save_png_bytes(image_bytes, output_path, resize_dims=resize_dims)
                    result = {
                        "status": "ok",
                        "file": str(output_path),
                        "input": str(input_path),
                        "requested_model": requested_model_input,
                        "actual_model": model,
                        "prompt": prompt,
                        "prompt_file": str(saved_prompt_path) if saved_prompt_path else None,
                        "image_size": f"{image.width}x{image.height}",
                        "total_images": 1 + len(ref_paths),
                    }
                    if requested_model_input != requested_model:
                        result["resolved_requested_model"] = requested_model
                    if mask_path:
                        result["mask"] = str(mask_path)
                    if ref_paths:
                        result["ref_images"] = [str(rp) for rp in ref_paths]
                    if resize_dims:
                        result["post_resize"] = f"{resize_dims[0]}x{resize_dims[1]}"
                    combined_warnings = option_warnings + extra_warnings
                    if combined_warnings:
                        result["warnings"] = combined_warnings
                    if model != requested_model:
                        result["fallback_from"] = requested_model
                    result["fallback_chain"] = models_to_try
                    result["models_tried"] = tried + [model]
                    telemetry_result = _track_template_usage_from_args(args, event="edit_success", command="edit")
                    if telemetry_result:
                        result["template_telemetry"] = telemetry_result
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

        error_msg = str(last_error)
        result = {
            "status": "error",
            "error": error_msg,
            "prompt": prompt,
            "prompt_file": str(saved_prompt_path) if saved_prompt_path else None,
            "requested_model": requested_model_input,
            "resolved_requested_model": requested_model,
            "retries_per_model": retries,
            "fallback_chain": models_to_try,
            "models_tried": tried,
        }
        hint = _provider_error_hint(config_data, error_msg)
        if hint:
            result["hint"] = hint
        print(json.dumps(result, ensure_ascii=False))
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

    client = get_client(config_data)

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
                        "prompt_file": str(saved_prompt_path) if saved_prompt_path else None,
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
                    "prompt_file": str(saved_prompt_path) if saved_prompt_path else None,
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
                telemetry_result = _track_template_usage_from_args(args, event="edit_success", command="edit")
                if telemetry_result:
                    result["template_telemetry"] = telemetry_result
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
    else:
        hint = _provider_error_hint(config_data, error_msg)

    result = {
        "status": "error",
        "error": error_msg,
        "prompt": prompt,
        "prompt_file": str(saved_prompt_path) if saved_prompt_path else None,
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
    """Attempt image generation with a single model."""
    from google.genai import types

    return gemini_provider.try_generate(client, types, model, prompt, aspect_ratio, image_size=image_size)

def cmd_generate(args):
    """Generate an image from a text prompt, with automatic model fallback."""
    try:
        native_image_size, resize_dims, option_warnings = _resolve_image_request_options(args)
    except ValueError as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    config = _apply_command_provider_override(load_config(getattr(args, "config", None)), getattr(args, "provider", None))
    runtime_support = _runtime_support_status(config)
    if getattr(args, "dry_run", False):
        requested_model_input = _resolve_default_model(config, args.model)
        requested_model = _canonicalize_model(requested_model_input)
        prompt_archive = None
        if _prompt_archive_requested(args):
            prompt_archive = str(_resolve_prompt_archive_path(args.prompt, command="generate", prompt_output=getattr(args, "prompt_output", None)))
        print(json.dumps({
            "status": "ok",
            "dry_run": True,
            "command": "generate",
            "provider": runtime_support["provider"],
            "transport": runtime_support["transport"],
            "requested_model": requested_model_input,
            "resolved_model": requested_model,
            "prompt": args.prompt,
            "prompt_archive": prompt_archive,
            "aspect_ratio": args.aspect or "1:1",
            "native_image_size": native_image_size,
            "post_resize": f"{resize_dims[0]}x{resize_dims[1]}" if resize_dims else None,
            "fallback_chain": [requested_model] if getattr(args, "no_fallback", False) else _dedupe_preserve_order([requested_model] + _get_fallback_models(requested_model, runtime_support["provider"])),
            "provider_options": {
                "openai_size": getattr(args, "openai_size", None),
                "quality": getattr(args, "quality", None),
                "background": getattr(args, "background", None),
                "output_format": getattr(args, "output_format", None),
                "output_compression": getattr(args, "output_compression", None),
            },
            "warnings": option_warnings,
        }, ensure_ascii=False))
        return

    client = None
    if runtime_support["transport"] == TRANSPORT_GENAI:
        client = get_client(config)

    requested_model_input = _resolve_default_model(config, args.model)
    requested_model = _canonicalize_model(requested_model_input)
    prompt = args.prompt
    aspect_ratio = args.aspect or "1:1"
    no_fallback = getattr(args, "no_fallback", False)
    retries = getattr(args, "retries", 1)

    # Determine output path (default: current working directory with model name)
    user_output = args.output
    saved_prompt_path = _archive_prompt_for_command(
        args,
        prompt,
        "generate",
        metadata={
            "provider": runtime_support["provider"],
            "requested_model": requested_model_input,
            "aspect_ratio": aspect_ratio,
        },
    )

    # Build model attempt list
    if no_fallback:
        models_to_try = [requested_model]
    else:
        models_to_try = _dedupe_preserve_order([requested_model] + _get_fallback_models(requested_model, runtime_support["provider"]))

    tried = []
    last_error = None

    for model in models_to_try:
        # Retry same model up to (1 + retries) times before fallback
        for attempt in range(1 + retries):
            try:
                extra_warnings = []
                if runtime_support["provider"] == PROVIDER_CHATGPT_COMPATIBLE:
                    image_bytes, extra_warnings, gen_error = _chatgpt_try_generate(
                        config,
                        model,
                        prompt,
                    )
                    image_part = None
                elif runtime_support["transport"] == TRANSPORT_OPENAI_REST:
                    image_bytes, extra_warnings, gen_error = _openai_try_generate(
                        config,
                        model,
                        prompt,
                        aspect_ratio,
                        image_size=native_image_size,
                        openai_size=getattr(args, "openai_size", None),
                        quality=getattr(args, "quality", None),
                        background=getattr(args, "background", None),
                        output_format=getattr(args, "output_format", None),
                        output_compression=getattr(args, "output_compression", None),
                    )
                    image_part = None
                else:
                    image_part, gen_error = _try_generate(
                        client,
                        model,
                        prompt,
                        aspect_ratio,
                        image_size=native_image_size,
                    )
                    image_bytes = image_part.inline_data.data if image_part else None

                if gen_error and runtime_support["provider"] == PROVIDER_CHATGPT_COMPATIBLE and extra_warnings:
                    output_path = Path(user_output) if user_output else _default_output_path("bananahub_chatgpt_url", model).with_suffix(".url.txt")
                    if output_path.suffix.lower() != ".txt":
                        output_path = output_path.with_suffix(output_path.suffix + ".url.txt")
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(
                        json.dumps({"error": gen_error, "image_reference": extra_warnings[0]}, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    print(json.dumps({
                        "status": "partial",
                        "file": str(output_path),
                        "requested_model": requested_model_input,
                        "actual_model": model,
                        "prompt": prompt,
                        "prompt_file": str(saved_prompt_path) if saved_prompt_path else None,
                        "warning": "Chat response contained an image reference, but BananaHub could not download it. Saved reference metadata instead.",
                        "details": extra_warnings,
                    }, ensure_ascii=False))
                    return

                if gen_error:
                    # Content policy / no image — not a server error, don't fallback
                    error_payload = {
                        "status": "error",
                        "error": gen_error,
                        "prompt": prompt,
                        "prompt_file": str(saved_prompt_path) if saved_prompt_path else None,
                        "requested_model": requested_model_input,
                        "actual_model": model,
                    }
                    if extra_warnings:
                        error_payload["details"] = extra_warnings
                    print(json.dumps(error_payload, ensure_ascii=False))
                    sys.exit(1)

                # Success — resolve output path now that we know the actual model
                if user_output:
                    output_path = Path(user_output)
                else:
                    output_path = _default_output_path("bananahub", model)

                image = _save_png_bytes(image_bytes, output_path, resize_dims=resize_dims)

                result = {
                    "status": "ok",
                    "file": str(output_path),
                    "requested_model": requested_model_input,
                    "actual_model": model,
                    "prompt": prompt,
                    "prompt_file": str(saved_prompt_path) if saved_prompt_path else None,
                    "aspect_ratio": aspect_ratio,
                    "image_size": f"{image.width}x{image.height}",
                }
                if requested_model_input != requested_model:
                    result["resolved_requested_model"] = requested_model
                if native_image_size:
                    result["native_image_size"] = native_image_size
                if resize_dims:
                    result["post_resize"] = f"{resize_dims[0]}x{resize_dims[1]}"
                combined_warnings = option_warnings + extra_warnings
                if combined_warnings:
                    result["warnings"] = combined_warnings
                if model != requested_model:
                    result["fallback_from"] = requested_model
                result["fallback_chain"] = models_to_try
                result["models_tried"] = tried + [model]
                telemetry_result = _track_template_usage_from_args(args, event="generate_success", command="generate")
                if telemetry_result:
                    result["template_telemetry"] = telemetry_result
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
    else:
        hint = _provider_error_hint(config, error_msg)

    result = {
        "status": "error",
        "error": error_msg,
        "prompt": prompt,
        "prompt_file": str(saved_prompt_path) if saved_prompt_path else None,
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
    parser = argparse.ArgumentParser(prog="bananahub.py", description="BananaHub - provider-backed image generation")
    parser.add_argument("--config", help="Path to config file (JSON or .env)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate an image from a prompt")
    gen_parser.add_argument("prompt", help="Text prompt for image generation")
    gen_parser.add_argument("--provider", choices=sorted(SUPPORTED_PROVIDERS), help="Provider override for this command")
    gen_parser.add_argument("--model", "-m", help="Model ID (default depends on provider)")
    gen_parser.add_argument("--aspect", "-a", help="Aspect ratio, e.g. 1:1, 16:9, 9:16 (default: 1:1)")
    gen_parser.add_argument("--image-size", help="Native image-size preset: 1K, 2K, or 4K")
    gen_parser.add_argument("--openai-size", help="OpenAI-native size, e.g. 1024x1024 or model-supported custom size")
    gen_parser.add_argument("--quality", help="Provider-native quality preset, e.g. low/medium/high/auto")
    gen_parser.add_argument("--background", help="Provider-native background option, e.g. transparent/opaque/auto")
    gen_parser.add_argument("--output-format", help="Provider-native output format, e.g. png/jpeg/webp")
    gen_parser.add_argument("--output-compression", type=int, help="Provider-native output compression when supported")
    gen_parser.add_argument("--resize", help="Post-process resize to WxH, e.g. 1024x1024")
    gen_parser.add_argument("--size", "-s", help="Legacy compatibility flag: use 1K/2K/4K for native image size, or WxH for post-processing resize")
    gen_parser.add_argument("--output", "-o", help="Output file path (default: current directory)")
    gen_parser.add_argument("--save-prompt", action="store_true", help=f"Save the final prompt under {DEFAULT_PROMPT_ARCHIVE_DIR}/")
    gen_parser.add_argument("--prompt-output", help="Save the final prompt to a file or directory")
    gen_parser.add_argument("--no-fallback", action="store_true", help="Disable automatic model fallback on server errors")
    gen_parser.add_argument("--retries", type=int, default=1, help="Retry count per model on transient server/network errors before fallback (default: 1)")
    gen_parser.add_argument("--dry-run", action="store_true", help="Resolve config/model/options without calling the provider")
    _add_template_telemetry_flags(gen_parser)

    # edit command
    edit_parser = subparsers.add_parser("edit", help="Edit an existing image with a text prompt")
    edit_parser.add_argument("prompt", help="Text prompt describing the edit")
    edit_parser.add_argument("--input", "-i", required=True, help="Path to the source image")
    edit_parser.add_argument("--mask", help="Optional mask image for OpenAI-native mask edits")
    edit_parser.add_argument("--ref", "-r", nargs="+", default=[], help="Reference image paths (up to 13 additional images for style/content guidance)")
    edit_parser.add_argument("--provider", choices=sorted(SUPPORTED_PROVIDERS), help="Provider override for this command")
    edit_parser.add_argument("--model", "-m", help="Model ID (default depends on provider)")
    edit_parser.add_argument("--image-size", help="Native image-size preset: 1K, 2K, or 4K")
    edit_parser.add_argument("--resize", help="Post-process resize to WxH, e.g. 1024x1024")
    edit_parser.add_argument("--size", "-s", help="Legacy compatibility flag: use 1K/2K/4K for native image size, or WxH for post-processing resize")
    edit_parser.add_argument("--output", "-o", help="Output file path (default: current directory)")
    edit_parser.add_argument("--save-prompt", action="store_true", help=f"Save the final prompt under {DEFAULT_PROMPT_ARCHIVE_DIR}/")
    edit_parser.add_argument("--prompt-output", help="Save the final prompt to a file or directory")
    edit_parser.add_argument("--no-fallback", action="store_true", help="Disable automatic model fallback on server errors")
    edit_parser.add_argument("--retries", type=int, default=1, help="Retry count per model on transient server/network errors before fallback (default: 1)")
    edit_parser.add_argument("--dry-run", action="store_true", help="Resolve config/model/options without calling the provider")
    _add_template_telemetry_flags(edit_parser)

    # models command
    models_parser = subparsers.add_parser("models", help="List available models")
    models_parser.add_argument("--provider", choices=sorted(SUPPORTED_PROVIDERS), help="Provider override for this command")

    # check-mode command
    check_mode_parser = subparsers.add_parser("check-mode", help="Report runtime mode and capability layers")
    check_mode_parser.add_argument("--provider", choices=sorted(SUPPORTED_PROVIDERS), help="Provider override for this command")
    check_mode_parser.add_argument("--host-imagegen", action="store_true", help="Tell BananaHub that the host has a native image generation tool")
    check_mode_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    # init command
    init_parser = subparsers.add_parser("init", help="Check environment and guide setup")
    init_parser.add_argument("--skip-test", action="store_true", help="Skip API connectivity test")

    # config command
    config_parser = subparsers.add_parser("config", help="Show or persist BananaHub config")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config actions")

    config_show_parser = config_subparsers.add_parser("show", help="Show effective config resolution")
    config_show_parser.set_defaults(config_handler=cmd_config_show)

    config_set_parser = config_subparsers.add_parser("set", help="Write ~/.config/bananahub/config.json")
    config_set_parser.add_argument(
        "--provider",
        choices=sorted(SUPPORTED_PROVIDERS),
        help="Provider to persist",
    )
    config_set_parser.add_argument(
        "--auth-mode",
        choices=sorted(SUPPORTED_AUTH_MODES),
        help="Auth mode to persist: api_key or adc",
    )
    config_set_parser.add_argument("--profile", help="Named provider profile to update")
    config_set_parser.add_argument("--default-profile", help="Persist the default named provider profile")
    config_set_parser.add_argument("--api-key", help="API key to persist in BananaHub config or selected profile")
    config_set_parser.add_argument("--base-url", help="Custom Gemini-compatible base URL to persist")
    config_set_parser.add_argument("--project", help="Google Cloud project to persist")
    config_set_parser.add_argument("--location", help="Google Cloud location to persist")
    config_set_parser.add_argument("--model", help="Default model to persist")
    config_set_parser.add_argument("--clear-base-url", action="store_true", help="Remove stored custom base URL")
    config_set_parser.add_argument("--clear-project", action="store_true", help="Remove stored Google Cloud project")
    config_set_parser.add_argument("--clear-location", action="store_true", help="Remove stored Google Cloud location")
    config_set_parser.add_argument("--clear-model", action="store_true", help="Remove stored default model")
    config_set_parser.set_defaults(config_handler=cmd_config_set)

    telemetry_parser = subparsers.add_parser("telemetry", help="BananaHub usage telemetry helpers")
    telemetry_subparsers = telemetry_parser.add_subparsers(dest="telemetry_command", help="Telemetry actions")

    telemetry_status_parser = telemetry_subparsers.add_parser("status", help="Show anonymous telemetry identity")
    telemetry_status_parser.set_defaults(telemetry_handler=cmd_telemetry_status)

    telemetry_track_parser = telemetry_subparsers.add_parser("track", help="Send a template telemetry event")
    telemetry_track_parser.add_argument("--event", required=True, choices=sorted(VALID_TELEMETRY_EVENTS), help="Telemetry event name")
    telemetry_track_parser.add_argument("--template-id", required=True, help="Template id")
    telemetry_track_parser.add_argument("--template-repo", default=DEFAULT_TEMPLATE_REPO, help="Template repo")
    telemetry_track_parser.add_argument(
        "--template-distribution",
        choices=sorted(VALID_TEMPLATE_DISTRIBUTIONS),
        help="Template distribution (bundled or remote)",
    )
    telemetry_track_parser.add_argument(
        "--template-source",
        choices=sorted(VALID_CATALOG_SOURCES),
        help="Template source layer (curated or discovered)",
    )
    telemetry_track_parser.add_argument("--command-name", help="Origin command name, e.g. use/generate/edit")
    telemetry_track_parser.set_defaults(telemetry_handler=cmd_telemetry_track)

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "edit":
        cmd_edit(args)
    elif args.command == "models":
        cmd_models(args)
    elif args.command == "check-mode":
        cmd_check_mode(args)
    elif args.command == "init":
        cmd_init(args)
    elif args.command == "config":
        handler = getattr(args, "config_handler", None)
        if not handler:
            config_parser.print_help()
            sys.exit(1)
        handler(args)
    elif args.command == "telemetry":
        handler = getattr(args, "telemetry_handler", None)
        if not handler:
            telemetry_parser.print_help()
            sys.exit(1)
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
