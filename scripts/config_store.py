"""Config loading, validation, and serialization for BananaHub."""

import json
import os
from pathlib import Path

import runtime_config as cfg


def read_json_file(path, required=False):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        if required:
            raise ValueError(f"Invalid JSON config: {exc}") from exc
        return {}
    if not isinstance(data, dict):
        if required:
            raise ValueError(f"Invalid JSON config: expected object at {path}")
        return {}
    return data


def write_json_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def resolve_profile_data(data, profile_name=None):
    if not isinstance(data, dict):
        return data
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        return data
    selected = profile_name or data.get("default_profile") or data.get("profile")
    if not selected:
        return data
    profile_data = profiles.get(selected)
    if not isinstance(profile_data, dict):
        return data
    merged = {key: value for key, value in data.items() if key != "profiles"}
    merged.update(profile_data)
    merged["default_profile"] = selected
    return merged


def normalize_model(value, canonicalize_model):
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    return canonicalize_model(normalized)


def normalize_config_value(env_key, value, canonicalize_model):
    if env_key in {"GOOGLE_GEMINI_BASE_URL", "OPENAI_BASE_URL", "BANANAHUB_CHATGPT_BASE_URL"}:
        return cfg.normalize_base_url(value)
    if env_key == "BANANAHUB_PROVIDER":
        return cfg.normalize_provider(value)
    if env_key == "BANANAHUB_TRANSPORT":
        return cfg.normalize_transport(value)
    if env_key == "BANANAHUB_AUTH_MODE":
        return cfg.normalize_auth_mode(value)
    if env_key == "BANANAHUB_MODEL":
        return normalize_model(value, canonicalize_model)
    if env_key == "GOOGLE_GENAI_USE_VERTEXAI":
        return "true" if cfg.is_truthy(value) else None
    normalized = str(value).strip()
    if not normalized:
        return None
    return normalized


def apply_json_config(config, resolved_from, data, source, canonicalize_model, profile_name=None):
    data = resolve_profile_data(data, profile_name or os.environ.get("BANANAHUB_PROFILE"))
    for json_key, env_key in cfg.CONFIG_KEY_MAP.items():
        value = data.get(json_key)
        if value in (None, ""):
            continue
        try:
            value = normalize_config_value(env_key, value, canonicalize_model)
        except ValueError:
            continue
        if value in (None, ""):
            continue
        config[env_key] = value
        resolved_from[env_key] = source


def apply_env_config(config, resolved_from, canonicalize_model):
    for env_key, aliases in cfg.ENV_KEY_ALIASES.items():
        for alias in aliases:
            value = os.environ.get(alias)
            if not value:
                continue
            try:
                value = normalize_config_value(env_key, value, canonicalize_model)
            except ValueError:
                continue
            if value in (None, ""):
                continue
            config[env_key] = value
            resolved_from[env_key] = f"env:{alias}"
            break


def apply_dotenv_values(config, resolved_from, dotenv_values, source, canonicalize_model):
    for env_key, aliases in cfg.ENV_KEY_ALIASES.items():
        for alias in aliases:
            value = dotenv_values.get(alias)
            if not value:
                continue
            try:
                value = normalize_config_value(env_key, value, canonicalize_model)
            except ValueError:
                continue
            if value in (None, ""):
                continue
            config[env_key] = value
            resolved_from[env_key] = source
            break


def finalize_config(config, resolved_from):
    provider = config.get("BANANAHUB_PROVIDER")
    if not provider:
        if cfg.is_truthy(config.get("GOOGLE_GENAI_USE_VERTEXAI")):
            provider = cfg.PROVIDER_VERTEX_AI
            provider_source = "inferred:GOOGLE_GENAI_USE_VERTEXAI"
        elif config.get("GOOGLE_CLOUD_PROJECT") or config.get("GOOGLE_CLOUD_LOCATION"):
            provider = cfg.PROVIDER_VERTEX_AI
            provider_source = "inferred:google-cloud"
        elif config.get("BANANAHUB_CHATGPT_API_KEY") and not config.get("GEMINI_API_KEY") and not config.get("OPENAI_API_KEY"):
            provider = cfg.PROVIDER_CHATGPT_COMPATIBLE
            provider_source = "inferred:BANANAHUB_CHATGPT_API_KEY"
        elif config.get("OPENAI_API_KEY") and not config.get("GEMINI_API_KEY"):
            provider = cfg.PROVIDER_OPENAI
            provider_source = "inferred:OPENAI_API_KEY"
        elif config.get("GOOGLE_GEMINI_BASE_URL"):
            provider = cfg.PROVIDER_GEMINI_COMPATIBLE
            provider_source = "inferred:base_url"
        else:
            provider = cfg.DEFAULT_PROVIDER
            provider_source = "default"
        config["BANANAHUB_PROVIDER"] = provider
        resolved_from.setdefault("BANANAHUB_PROVIDER", provider_source)

    transport = config.get("BANANAHUB_TRANSPORT")
    if not transport:
        config["BANANAHUB_TRANSPORT"] = cfg.DEFAULT_TRANSPORT_BY_PROVIDER.get(provider, cfg.TRANSPORT_GENAI)
        resolved_from.setdefault("BANANAHUB_TRANSPORT", f"default:{provider}")

    auth_mode = config.get("BANANAHUB_AUTH_MODE")
    if not auth_mode:
        if provider == cfg.PROVIDER_VERTEX_AI and not config.get("GEMINI_API_KEY"):
            auth_mode = cfg.AUTH_MODE_ADC
        else:
            auth_mode = cfg.AUTH_MODE_API_KEY
        config["BANANAHUB_AUTH_MODE"] = auth_mode
        resolved_from.setdefault("BANANAHUB_AUTH_MODE", f"default:{provider}")

    if provider == cfg.PROVIDER_VERTEX_AI and not config.get("GOOGLE_CLOUD_LOCATION"):
        config["GOOGLE_CLOUD_LOCATION"] = cfg.DEFAULT_LOCATION
        resolved_from.setdefault("GOOGLE_CLOUD_LOCATION", "default:vertex-ai")


def runtime_support_status(config):
    provider = config.get("BANANAHUB_PROVIDER", cfg.DEFAULT_PROVIDER)
    transport = config.get("BANANAHUB_TRANSPORT", cfg.DEFAULT_TRANSPORT_BY_PROVIDER.get(provider, cfg.TRANSPORT_GENAI))
    auth_mode = config.get("BANANAHUB_AUTH_MODE", cfg.AUTH_MODE_API_KEY)
    reasons = []
    capabilities = {"generate": True, "edit": True, "models": True, "healthcheck": True}

    if provider in {cfg.PROVIDER_GOOGLE_AI_STUDIO, cfg.PROVIDER_GEMINI_COMPATIBLE}:
        if transport != cfg.TRANSPORT_GENAI:
            reasons.append(f"provider '{provider}' requires transport '{cfg.TRANSPORT_GENAI}', not '{transport}'.")
        if auth_mode != cfg.AUTH_MODE_API_KEY:
            reasons.append(f"provider '{provider}' requires auth_mode '{cfg.AUTH_MODE_API_KEY}', not '{auth_mode}'.")
    elif provider == cfg.PROVIDER_VERTEX_AI:
        if transport != cfg.TRANSPORT_GENAI:
            reasons.append(f"provider '{provider}' requires transport '{cfg.TRANSPORT_GENAI}', not '{transport}'.")
        if auth_mode not in {cfg.AUTH_MODE_API_KEY, cfg.AUTH_MODE_ADC}:
            reasons.append(f"provider '{provider}' requires auth_mode '{cfg.AUTH_MODE_API_KEY}' or '{cfg.AUTH_MODE_ADC}', not '{auth_mode}'.")
    elif provider in {cfg.PROVIDER_OPENAI, cfg.PROVIDER_OPENAI_COMPATIBLE, cfg.PROVIDER_CHATGPT_COMPATIBLE}:
        if transport != cfg.TRANSPORT_OPENAI_REST:
            reasons.append(f"provider '{provider}' requires transport '{cfg.TRANSPORT_OPENAI_REST}', not '{transport}'.")
        if auth_mode != cfg.AUTH_MODE_API_KEY:
            reasons.append(f"provider '{provider}' requires auth_mode '{cfg.AUTH_MODE_API_KEY}', not '{auth_mode}'.")
        capabilities["edit"] = provider in {cfg.PROVIDER_OPENAI, cfg.PROVIDER_OPENAI_COMPATIBLE}
        capabilities["mask_edit"] = provider in {cfg.PROVIDER_OPENAI, cfg.PROVIDER_OPENAI_COMPATIBLE}
        if provider == cfg.PROVIDER_CHATGPT_COMPATIBLE:
            capabilities["edit"] = False
            capabilities["chat_image"] = True
    else:
        reasons.append(f"provider '{provider}' is not recognized by this BananaHub runtime.")

    return {
        "supported": not reasons,
        "provider": provider,
        "transport": transport,
        "auth_mode": auth_mode,
        "reasons": reasons,
        "capabilities": capabilities,
    }


def config_validation_errors(config):
    errors = []
    support = runtime_support_status(config)
    errors.extend(support["reasons"])
    if support["auth_mode"] == cfg.AUTH_MODE_API_KEY:
        if support["provider"] == cfg.PROVIDER_CHATGPT_COMPATIBLE and not config.get("BANANAHUB_CHATGPT_API_KEY"):
            errors.append("ChatGPT-compatible API key not found. Set BANANAHUB_CHATGPT_API_KEY.")
        elif support["provider"] == cfg.PROVIDER_OPENAI and not config.get("OPENAI_API_KEY"):
            errors.append("OpenAI API key not found. Set OPENAI_API_KEY or persist openai_api_key in BananaHub config.")
        elif support["provider"] not in {cfg.PROVIDER_OPENAI, cfg.PROVIDER_CHATGPT_COMPATIBLE} and not config.get("GEMINI_API_KEY"):
            errors.append("API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY, or persist api_key in BananaHub config.")
    if support["provider"] == cfg.PROVIDER_GEMINI_COMPATIBLE and not config.get("GOOGLE_GEMINI_BASE_URL"):
        errors.append("provider 'gemini-compatible' requires a base_url.")
    if support["provider"] == cfg.PROVIDER_CHATGPT_COMPATIBLE and not config.get("BANANAHUB_CHATGPT_BASE_URL"):
        errors.append("provider 'chatgpt-compatible' requires chatgpt_base_url or BANANAHUB_CHATGPT_BASE_URL.")
    if support["provider"] == cfg.PROVIDER_OPENAI_COMPATIBLE and not config.get("GOOGLE_GEMINI_BASE_URL") and not config.get("OPENAI_BASE_URL"):
        errors.append("provider 'openai-compatible' requires a base_url.")
    return errors


def resolve_default_model(config, cli_model=None, default_by_provider=None, default_model=None):
    if cli_model:
        return cli_model
    configured = config.get("BANANAHUB_MODEL")
    if configured:
        return configured
    return (default_by_provider or {}).get(config.get("BANANAHUB_PROVIDER", cfg.DEFAULT_PROVIDER), default_model)


def load_explicit_config(path, canonicalize_model, load_dotenv_fn):
    config = {}
    resolved_from = {}
    raw_text = path.read_text()
    stripped = raw_text.lstrip()
    if path.suffix == ".json" or stripped.startswith("{"):
        data = read_json_file(path, required=True)
        apply_json_config(config, resolved_from, data, str(path), canonicalize_model)
        return config, resolved_from
    apply_dotenv_values(config, resolved_from, load_dotenv_fn(path), str(path), canonicalize_model)
    return config, resolved_from


def load_merged_config(config_file, canonicalize_model, load_dotenv_fn, config_path=cfg.SKILL_CONFIG_PATH):
    config = {}
    resolved_from = {}
    explicit_resolved_from = {}
    existing_sources = []
    if config_path.exists():
        existing_sources.append(str(config_path))
        data = read_json_file(config_path)
        apply_json_config(config, resolved_from, data, str(config_path), canonicalize_model)
    apply_env_config(config, resolved_from, canonicalize_model)
    if config_file:
        cf = Path(config_file)
        if not cf.exists():
            raise FileNotFoundError(f"Config file not found: {cf}")
        explicit_config, explicit_resolved_from = load_explicit_config(cf, canonicalize_model, load_dotenv_fn)
        config.update(explicit_config)
        resolved_from.update(explicit_resolved_from)
        existing_sources.append(str(cf))
    explicit_resolved_from.update(resolved_from)
    finalize_config(config, resolved_from)
    deduped_sources = []
    for source in existing_sources:
        if source not in deduped_sources:
            deduped_sources.append(source)
    return config, resolved_from, deduped_sources, explicit_resolved_from


def apply_command_provider_override(config, provider):
    if not provider:
        return config
    updated = dict(config)
    normalized = cfg.normalize_provider(provider)
    updated["BANANAHUB_PROVIDER"] = normalized
    updated["BANANAHUB_TRANSPORT"] = cfg.DEFAULT_TRANSPORT_BY_PROVIDER.get(normalized, cfg.TRANSPORT_GENAI)
    if "BANANAHUB_AUTH_MODE" not in updated:
        updated["BANANAHUB_AUTH_MODE"] = cfg.AUTH_MODE_API_KEY
    return updated


def list_config_sources(config_sources, explicit_resolved_from):
    ordered = list(config_sources)
    for source in sorted(set(explicit_resolved_from.values())):
        if source not in ordered:
            ordered.append(source)
    return ordered


def serialize_resolved_from(resolved_from):
    return {
        "provider": resolved_from.get("BANANAHUB_PROVIDER"),
        "transport": resolved_from.get("BANANAHUB_TRANSPORT"),
        "auth_mode": resolved_from.get("BANANAHUB_AUTH_MODE"),
        "api_key": resolved_from.get("GEMINI_API_KEY") or resolved_from.get("OPENAI_API_KEY") or resolved_from.get("BANANAHUB_CHATGPT_API_KEY"),
        "base_url": resolved_from.get("GOOGLE_GEMINI_BASE_URL") or resolved_from.get("OPENAI_BASE_URL") or resolved_from.get("BANANAHUB_CHATGPT_BASE_URL"),
        "model": resolved_from.get("BANANAHUB_MODEL"),
        "profile": resolved_from.get("BANANAHUB_PROFILE"),
        "project": resolved_from.get("GOOGLE_CLOUD_PROJECT"),
        "location": resolved_from.get("GOOGLE_CLOUD_LOCATION"),
    }


def serialize_effective_config(config, chatgpt_base_url_fn):
    support = runtime_support_status(config)
    provider = support["provider"]
    endpoint_resolution = None
    base_url = None
    api_key = None
    api_key_type = None
    if provider == cfg.PROVIDER_CHATGPT_COMPATIBLE:
        base_url = config.get("BANANAHUB_CHATGPT_BASE_URL") or None
        api_key = config.get("BANANAHUB_CHATGPT_API_KEY") or None
        api_key_type = "chatgpt"
        if base_url:
            endpoint_resolution = {"configured_base_url": base_url, "resolved_base_url": chatgpt_base_url_fn(config)}
    elif provider == cfg.PROVIDER_OPENAI:
        base_url = config.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        api_key = config.get("OPENAI_API_KEY") or None
        api_key_type = "openai"
        endpoint_resolution = cfg.resolve_openai_endpoint(base_url)
    elif support["transport"] == cfg.TRANSPORT_OPENAI_REST:
        base_url = config.get("OPENAI_BASE_URL") or config.get("GOOGLE_GEMINI_BASE_URL") or None
        api_key = config.get("OPENAI_API_KEY") or config.get("GEMINI_API_KEY") or None
        api_key_type = "openai-compatible"
        if base_url:
            endpoint_resolution = cfg.resolve_openai_endpoint(base_url)
    else:
        base_url = config.get("GOOGLE_GEMINI_BASE_URL") or None
        api_key = config.get("GEMINI_API_KEY") or None
        api_key_type = "gemini"
        if base_url:
            endpoint_resolution = cfg.resolve_genai_endpoint(base_url)
    return {
        "provider": config.get("BANANAHUB_PROVIDER"),
        "transport": config.get("BANANAHUB_TRANSPORT"),
        "auth_mode": config.get("BANANAHUB_AUTH_MODE"),
        "api_key": cfg.mask_secret(api_key) if api_key else None,
        "api_key_type": api_key_type,
        "base_url": base_url,
        "model": config.get("BANANAHUB_MODEL") or None,
        "profile": config.get("BANANAHUB_PROFILE") or None,
        "project": config.get("GOOGLE_CLOUD_PROJECT") or None,
        "location": config.get("GOOGLE_CLOUD_LOCATION") or None,
        "capabilities": support["capabilities"],
        "endpoint_resolution": endpoint_resolution,
    }


def load_persisted_config_for_write(config_path=cfg.SKILL_CONFIG_PATH):
    if config_path.exists():
        return read_json_file(config_path, required=True)
    return {}


def write_persisted_config(data, config_path=cfg.SKILL_CONFIG_PATH):
    write_json_file(config_path, data)
