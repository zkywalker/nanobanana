#!/usr/bin/env python3
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("config_store", ROOT / "scripts" / "config_store.py")
config_store = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_store)


def canonicalize(value):
    aliases = {"gpt image 2": "gpt-image-2"}
    return aliases.get(value, value)


def test_profile_merge():
    data = {
        "default_profile": "gpt",
        "profiles": {
            "gpt": {"provider": "openai", "openai_api_key": "k", "model": "gpt image 2"},
            "nano": {"provider": "google-ai-studio", "api_key": "g"},
        },
    }
    config = {}
    resolved = {}
    config_store.apply_json_config(config, resolved, data, "test.json", canonicalize)
    assert config["BANANAHUB_PROVIDER"] == "openai"
    assert config["OPENAI_API_KEY"] == "k"
    assert config["BANANAHUB_MODEL"] == "gpt-image-2"


def test_chatgpt_inference_and_validation():
    config = {"BANANAHUB_CHATGPT_API_KEY": "k", "BANANAHUB_CHATGPT_BASE_URL": "https://example.com/api"}
    resolved = {}
    config_store.finalize_config(config, resolved)
    assert config["BANANAHUB_PROVIDER"] == "chatgpt-compatible"
    assert config_store.config_validation_errors(config) == []
    support = config_store.runtime_support_status(config)
    assert support["capabilities"]["chat_image"] is True
    assert support["capabilities"]["edit"] is False


def test_openai_compatible_exposes_images_api_edit_capabilities():
    config = {
        "BANANAHUB_PROVIDER": "openai-compatible",
        "BANANAHUB_TRANSPORT": "openai-rest",
        "BANANAHUB_AUTH_MODE": "api_key",
        "GEMINI_API_KEY": "k",
        "OPENAI_BASE_URL": "https://example.com/v1",
    }
    support = config_store.runtime_support_status(config)

    assert support["supported"] is True
    assert support["capabilities"]["edit"] is True
    assert support["capabilities"]["mask_edit"] is True


def test_empty_config_defaults_to_openai_compatible_gpt_path():
    config = {}
    resolved = {}
    config_store.finalize_config(config, resolved)

    assert config["BANANAHUB_PROVIDER"] == "openai-compatible"
    assert config["BANANAHUB_TRANSPORT"] == "openai-rest"
    assert resolved["BANANAHUB_PROVIDER"] == "default"


def test_openai_base_url_infers_openai_compatible_provider():
    config = {"OPENAI_BASE_URL": "https://gateway.example/v1", "OPENAI_API_KEY": "k"}
    resolved = {"OPENAI_BASE_URL": "env:OPENAI_BASE_URL", "OPENAI_API_KEY": "env:OPENAI_API_KEY"}
    config_store.finalize_config(config, resolved)

    assert config["BANANAHUB_PROVIDER"] == "openai-compatible"
    assert resolved["BANANAHUB_PROVIDER"] == "inferred:OPENAI_BASE_URL"


def test_existing_gemini_key_keeps_google_ai_studio_provider():
    config = {"GEMINI_API_KEY": "k"}
    resolved = {"GEMINI_API_KEY": "config.json"}
    config_store.finalize_config(config, resolved)

    assert config["BANANAHUB_PROVIDER"] == "google-ai-studio"
    assert resolved["BANANAHUB_PROVIDER"] == "inferred:GEMINI_API_KEY"


def test_openai_compatible_accepts_openai_api_key():
    config = {
        "BANANAHUB_PROVIDER": "openai-compatible",
        "BANANAHUB_TRANSPORT": "openai-rest",
        "BANANAHUB_AUTH_MODE": "api_key",
        "OPENAI_API_KEY": "k",
        "OPENAI_BASE_URL": "https://gateway.example/v1",
    }

    assert config_store.config_validation_errors(config) == []


def test_resolved_from_is_provider_scoped_and_ignored_sources_are_explicit():
    config = {
        "BANANAHUB_PROVIDER": "google-ai-studio",
        "BANANAHUB_TRANSPORT": "genai",
        "BANANAHUB_AUTH_MODE": "api_key",
        "GEMINI_API_KEY": "gemini-key",
        "BANANAHUB_CHATGPT_API_KEY": "chat-key",
        "BANANAHUB_CHATGPT_BASE_URL": "https://chat.example/v1",
    }
    resolved = {
        "BANANAHUB_PROVIDER": "config.json",
        "BANANAHUB_TRANSPORT": "default:google-ai-studio",
        "BANANAHUB_AUTH_MODE": "default:google-ai-studio",
        "GEMINI_API_KEY": "config.json",
        "BANANAHUB_CHATGPT_API_KEY": "env:BANANAHUB_CHATGPT_API_KEY",
        "BANANAHUB_CHATGPT_BASE_URL": "env:BANANAHUB_CHATGPT_BASE_URL",
    }

    serialized = config_store.serialize_resolved_from(config, resolved)
    ignored = config_store.inactive_config_sources(config, resolved)

    assert serialized["api_key"] == "config.json"
    assert serialized["base_url"] is None
    assert {
        "field": "chatgpt_base_url",
        "internal_key": "BANANAHUB_CHATGPT_BASE_URL",
        "source": "env:BANANAHUB_CHATGPT_BASE_URL",
        "reason": "inactive for selected provider",
    } in ignored


def test_command_provider_override():
    config = {"BANANAHUB_PROVIDER": "google-ai-studio", "BANANAHUB_TRANSPORT": "genai"}
    updated = config_store.apply_command_provider_override(config, "openai")
    assert updated["BANANAHUB_PROVIDER"] == "openai"
    assert updated["BANANAHUB_TRANSPORT"] == "openai-rest"
    assert config["BANANAHUB_PROVIDER"] == "google-ai-studio"


def test_persisted_config_roundtrip(tmp_path=None):
    if tmp_path is None:
        import tempfile

        tmp_dir = tempfile.TemporaryDirectory()
        config_path = Path(tmp_dir.name) / "config.json"
    else:
        tmp_dir = None
        config_path = tmp_path / "config.json"

    data = {
        "default_profile": "chat",
        "profiles": {
            "chat": {
                "provider": "chatgpt-compatible",
                "chatgpt_api_key": "test-key",
                "chatgpt_base_url": "https://example.com/chatgpt-api",
                "model": "gpt-5.4",
            }
        },
    }

    try:
        config_store.write_persisted_config(data, config_path=config_path)
        loaded = config_store.load_persisted_config_for_write(config_path=config_path)
        assert loaded == data

        config = {}
        resolved = {}
        config_store.apply_json_config(config, resolved, loaded, str(config_path), canonicalize)
        config_store.finalize_config(config, resolved)
        assert config["BANANAHUB_PROVIDER"] == "chatgpt-compatible"
        assert config["BANANAHUB_CHATGPT_API_KEY"] == "test-key"
        assert config["BANANAHUB_CHATGPT_BASE_URL"] == "https://example.com/chatgpt-api"
        assert config["BANANAHUB_MODEL"] == "gpt-5.4"
    finally:
        if tmp_dir is not None:
            tmp_dir.cleanup()


if __name__ == "__main__":
    test_profile_merge()
    test_chatgpt_inference_and_validation()
    test_openai_compatible_exposes_images_api_edit_capabilities()
    test_empty_config_defaults_to_openai_compatible_gpt_path()
    test_openai_base_url_infers_openai_compatible_provider()
    test_existing_gemini_key_keeps_google_ai_studio_provider()
    test_openai_compatible_accepts_openai_api_key()
    test_resolved_from_is_provider_scoped_and_ignored_sources_are_explicit()
    test_command_provider_override()
    test_persisted_config_roundtrip()
    print("ok")
