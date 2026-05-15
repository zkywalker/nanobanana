"""Runtime configuration constants and pure helpers for BananaHub."""

import re
from pathlib import Path
from urllib.parse import urlparse, urlunparse

SKILL_CONFIG_DIR = Path.home() / ".config" / "bananahub"
SKILL_CONFIG_PATH = SKILL_CONFIG_DIR / "config.json"
TELEMETRY_STATE_PATH = SKILL_CONFIG_DIR / "telemetry.json"

PROVIDER_GOOGLE_AI_STUDIO = "google-ai-studio"
PROVIDER_GEMINI_COMPATIBLE = "gemini-compatible"
PROVIDER_VERTEX_AI = "vertex-ai"
PROVIDER_OPENAI = "openai"
PROVIDER_OPENAI_COMPATIBLE = "openai-compatible"
PROVIDER_CHATGPT_COMPATIBLE = "chatgpt-compatible"
SUPPORTED_PROVIDERS = {
    PROVIDER_GOOGLE_AI_STUDIO,
    PROVIDER_GEMINI_COMPATIBLE,
    PROVIDER_VERTEX_AI,
    PROVIDER_OPENAI,
    PROVIDER_OPENAI_COMPATIBLE,
    PROVIDER_CHATGPT_COMPATIBLE,
}
SUPPORTED_RUNTIME_PROVIDERS = set(SUPPORTED_PROVIDERS)
DEFAULT_PROVIDER = PROVIDER_OPENAI_COMPATIBLE
DEFAULT_LOCATION = "global"

TRANSPORT_GENAI = "genai"
TRANSPORT_GEMINI_REST = "gemini-rest"
TRANSPORT_OPENAI_REST = "openai-rest"
SUPPORTED_TRANSPORTS = {TRANSPORT_GENAI, TRANSPORT_GEMINI_REST, TRANSPORT_OPENAI_REST}

AUTH_MODE_API_KEY = "api_key"
AUTH_MODE_ADC = "adc"
SUPPORTED_AUTH_MODES = {AUTH_MODE_API_KEY, AUTH_MODE_ADC}

PROVIDER_ALIASES = {
    "google": PROVIDER_GOOGLE_AI_STUDIO,
    "google-ai": PROVIDER_GOOGLE_AI_STUDIO,
    "google-ai-studio": PROVIDER_GOOGLE_AI_STUDIO,
    "ai-studio": PROVIDER_GOOGLE_AI_STUDIO,
    "gemini-developer-api": PROVIDER_GOOGLE_AI_STUDIO,
    "developer-api": PROVIDER_GOOGLE_AI_STUDIO,
    "gemini-compatible": PROVIDER_GEMINI_COMPATIBLE,
    "compatible": PROVIDER_GEMINI_COMPATIBLE,
    "proxy": PROVIDER_GEMINI_COMPATIBLE,
    "relay": PROVIDER_GEMINI_COMPATIBLE,
    "custom-endpoint": PROVIDER_GEMINI_COMPATIBLE,
    "vertex": PROVIDER_VERTEX_AI,
    "vertex-ai": PROVIDER_VERTEX_AI,
    "openai": PROVIDER_OPENAI,
    "openai-official": PROVIDER_OPENAI,
    "openai-compatible": PROVIDER_OPENAI_COMPATIBLE,
    "chatgpt-compatible": PROVIDER_CHATGPT_COMPATIBLE,
    "chatgpt": PROVIDER_CHATGPT_COMPATIBLE,
}
TRANSPORT_ALIASES = {
    "genai": TRANSPORT_GENAI,
    "gemini": TRANSPORT_GEMINI_REST,
    "gemini-rest": TRANSPORT_GEMINI_REST,
    "openai": TRANSPORT_OPENAI_REST,
    "openai-rest": TRANSPORT_OPENAI_REST,
}
AUTH_MODE_ALIASES = {
    "api_key": AUTH_MODE_API_KEY,
    "apikey": AUTH_MODE_API_KEY,
    "key": AUTH_MODE_API_KEY,
    "adc": AUTH_MODE_ADC,
}
DEFAULT_TRANSPORT_BY_PROVIDER = {
    PROVIDER_GOOGLE_AI_STUDIO: TRANSPORT_GENAI,
    PROVIDER_GEMINI_COMPATIBLE: TRANSPORT_GENAI,
    PROVIDER_VERTEX_AI: TRANSPORT_GENAI,
    PROVIDER_OPENAI: TRANSPORT_OPENAI_REST,
    PROVIDER_OPENAI_COMPATIBLE: TRANSPORT_OPENAI_REST,
    PROVIDER_CHATGPT_COMPATIBLE: TRANSPORT_OPENAI_REST,
}

CONFIG_KEY_MAP = {
    "provider": "BANANAHUB_PROVIDER",
    "transport": "BANANAHUB_TRANSPORT",
    "auth_mode": "BANANAHUB_AUTH_MODE",
    "api_key": "GEMINI_API_KEY",
    "openai_api_key": "OPENAI_API_KEY",
    "chatgpt_api_key": "BANANAHUB_CHATGPT_API_KEY",
    "google_api_key": "GEMINI_API_KEY",
    "gemini_api_key": "GEMINI_API_KEY",
    "base_url": "GOOGLE_GEMINI_BASE_URL",
    "openai_base_url": "OPENAI_BASE_URL",
    "chatgpt_base_url": "BANANAHUB_CHATGPT_BASE_URL",
    "chatgpt_user_agent": "BANANAHUB_CHATGPT_USER_AGENT",
    "chatgpt_referer": "BANANAHUB_CHATGPT_REFERER",
    "gemini_base_url": "GOOGLE_GEMINI_BASE_URL",
    "project": "GOOGLE_CLOUD_PROJECT",
    "location": "GOOGLE_CLOUD_LOCATION",
    "model": "BANANAHUB_MODEL",
    "default_profile": "BANANAHUB_PROFILE",
    "use_vertexai": "GOOGLE_GENAI_USE_VERTEXAI",
}

ENV_KEY_ALIASES = {
    "BANANAHUB_PROVIDER": ("BANANAHUB_PROVIDER",),
    "BANANAHUB_TRANSPORT": ("BANANAHUB_TRANSPORT",),
    "BANANAHUB_AUTH_MODE": ("BANANAHUB_AUTH_MODE",),
    "BANANAHUB_MODEL": ("BANANAHUB_MODEL",),
    "BANANAHUB_PROFILE": ("BANANAHUB_PROFILE",),
    "GEMINI_API_KEY": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "OPENAI_API_KEY": ("OPENAI_API_KEY",),
    "BANANAHUB_CHATGPT_API_KEY": ("BANANAHUB_CHATGPT_API_KEY", "CHATGPT_COMPATIBLE_API_KEY"),
    "OPENAI_BASE_URL": ("OPENAI_BASE_URL",),
    "BANANAHUB_CHATGPT_BASE_URL": ("BANANAHUB_CHATGPT_BASE_URL", "CHATGPT_COMPATIBLE_BASE_URL"),
    "BANANAHUB_CHATGPT_USER_AGENT": ("BANANAHUB_CHATGPT_USER_AGENT", "CHATGPT_COMPATIBLE_USER_AGENT"),
    "BANANAHUB_CHATGPT_REFERER": ("BANANAHUB_CHATGPT_REFERER", "CHATGPT_COMPATIBLE_REFERER"),
    "GOOGLE_GEMINI_BASE_URL": ("GOOGLE_GEMINI_BASE_URL", "GEMINI_BASE_URL", "BANANAHUB_BASE_URL"),
    "GOOGLE_CLOUD_PROJECT": ("GOOGLE_CLOUD_PROJECT",),
    "GOOGLE_CLOUD_LOCATION": ("GOOGLE_CLOUD_LOCATION", "GOOGLE_CLOUD_REGION"),
    "GOOGLE_GENAI_USE_VERTEXAI": ("GOOGLE_GENAI_USE_VERTEXAI",),
}

ENV_OVERRIDE_FLAG = "BANANAHUB_ENV_OVERRIDE"


def mask_secret(value):
    if not value:
        return ""
    if len(value) <= 12:
        return "***"
    return value[:8] + "..." + value[-4:]


def normalize_base_url(value):
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    if not re.match(r"^https?://", normalized):
        raise ValueError("base_url must start with http:// or https://")
    return normalized.rstrip("/")


def split_trailing_api_version(base_url, default_api_version="v1beta"):
    normalized = normalize_base_url(base_url)
    if not normalized:
        return None, default_api_version, False
    parsed = urlparse(normalized)
    path = parsed.path.rstrip("/")
    match = re.search(r"/(v\d+(?:beta\d*|alpha\d*)?)$", path)
    if not match:
        return normalized, default_api_version, False
    api_version = match.group(1)
    base_path = path[: -(len(api_version) + 1)]
    rebuilt = urlunparse(parsed._replace(path=base_path))
    return rebuilt.rstrip("/"), api_version, True


def resolve_genai_endpoint(base_url):
    if not base_url:
        return {"configured_base_url": None, "resolved_base_url": None, "api_version": "v1beta", "warnings": []}
    resolved_base_url, api_version, stripped_version = split_trailing_api_version(base_url)
    warnings = []
    if stripped_version:
        warnings.append(f"Detected trailing `/{api_version}` in base_url and normalized it to avoid duplicating the API version.")
    return {
        "configured_base_url": normalize_base_url(base_url),
        "resolved_base_url": resolved_base_url,
        "api_version": api_version,
        "warnings": warnings,
    }


def resolve_openai_endpoint(base_url):
    configured = normalize_base_url(base_url)
    parsed = urlparse(configured)
    path = parsed.path.rstrip("/")
    warnings = []
    if parsed.netloc == "generativelanguage.googleapis.com":
        if path in {"", "/v1beta", "/v1beta1", "/v1"}:
            suffix = "/v1beta/openai"
            warnings.append("Expanded the official Gemini OpenAI-compatible endpoint to `/v1beta/openai`.")
        elif path == "/openai":
            suffix = "/v1beta/openai"
            warnings.append("Expanded `/openai` to the official Gemini path `/v1beta/openai`.")
        else:
            suffix = path or "/v1beta/openai"
        resolved = urlunparse(parsed._replace(path=suffix))
        return {"configured_base_url": configured, "resolved_base_url": resolved.rstrip("/"), "warnings": warnings}
    if path in {"", "/"}:
        resolved = urlunparse(parsed._replace(path="/v1"))
        warnings.append("Appended `/v1` to the OpenAI-compatible base_url.")
        return {"configured_base_url": configured, "resolved_base_url": resolved.rstrip("/"), "warnings": warnings}
    if path == "/openai":
        resolved = urlunparse(parsed._replace(path="/openai/v1"))
        warnings.append("Appended `/v1` to the OpenAI-compatible `/openai` base_url.")
        return {"configured_base_url": configured, "resolved_base_url": resolved.rstrip("/"), "warnings": warnings}
    return {"configured_base_url": configured, "resolved_base_url": configured, "warnings": warnings}


def normalize_provider(value):
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    normalized = PROVIDER_ALIASES.get(normalized, normalized)
    if normalized not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise ValueError(f"provider must be one of: {supported}")
    return normalized


def normalize_transport(value):
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    normalized = TRANSPORT_ALIASES.get(normalized, normalized)
    if normalized not in SUPPORTED_TRANSPORTS:
        supported = ", ".join(sorted(SUPPORTED_TRANSPORTS))
        raise ValueError(f"transport must be one of: {supported}")
    return normalized


def normalize_auth_mode(value):
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    normalized = AUTH_MODE_ALIASES.get(normalized, normalized)
    if normalized not in SUPPORTED_AUTH_MODES:
        supported = ", ".join(sorted(SUPPORTED_AUTH_MODES))
        raise ValueError(f"auth_mode must be one of: {supported}")
    return normalized


def is_truthy(value):
    normalized = str(value or "").strip().lower()
    return normalized in {"1", "true", "yes", "on"}
