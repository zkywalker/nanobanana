#!/usr/bin/env python3
import importlib.util
import json
import os
from contextlib import redirect_stdout
from io import StringIO
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "bananahub.py"
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("bananahub", MODULE_PATH)
bananahub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bananahub)


class TempHome:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_home = os.environ.get("HOME")
        os.environ["HOME"] = self.tmp.name
        self.old_dir = bananahub.SKILL_CONFIG_DIR
        self.old_path = bananahub.SKILL_CONFIG_PATH
        self.old_telemetry = bananahub.TELEMETRY_STATE_PATH
        new_dir = Path(self.tmp.name) / ".config" / "bananahub"
        bananahub.SKILL_CONFIG_DIR = new_dir
        bananahub.SKILL_CONFIG_PATH = new_dir / "config.json"
        bananahub.TELEMETRY_STATE_PATH = new_dir / "telemetry.json"
        return bananahub.SKILL_CONFIG_PATH

    def __exit__(self, exc_type, exc, tb):
        bananahub.SKILL_CONFIG_DIR = self.old_dir
        bananahub.SKILL_CONFIG_PATH = self.old_path
        bananahub.TELEMETRY_STATE_PATH = self.old_telemetry
        if self.old_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = self.old_home
        self.tmp.cleanup()


class Args:
    pass


def quickset_args(**overrides):
    args = Args()
    args.provider = "openai-compatible"
    args.profile = None
    args.default_profile = True
    args.api_key = "test-key"
    args.base_url = "https://token.bigfish.space/v1"
    args.model = None
    args.auth_mode = None
    args.project = None
    args.location = None
    for key, value in overrides.items():
        setattr(args, key, value)
    return args


def test_quickset_openai_compatible_writes_gpt_profile():
    with TempHome() as config_path:
        persisted = bananahub._load_persisted_for_update_or_exit()
        target = bananahub._apply_config_updates(
            persisted,
            provider="openai-compatible",
            api_key="test-key",
            base_url="https://token.bigfish.space/v1",
            model="gpt-image-2",
            auth_mode="api_key",
            profile="gpt",
            default_profile="gpt",
        )
        assert bananahub._validate_persisted_target_config(target) is None
        bananahub._write_persisted_config_secure(persisted)
        raw = json.loads(config_path.read_text())

    assert raw == {
        "profiles": {
            "gpt": {
                "provider": "openai-compatible",
                "auth_mode": "api_key",
                "openai_api_key": "test-key",
                "model": "gpt-image-2",
                "openai_base_url": "https://token.bigfish.space/v1",
            }
        },
        "default_profile": "gpt",
    }


def test_quickset_defaults_openai_compatible_to_gpt_image_2():
    assert bananahub.DEFAULT_PROVIDER == "openai-compatible"
    assert bananahub.DEFAULT_MODEL == "gpt-image-2"
    assert bananahub._provider_default_model("openai-compatible") == "gpt-image-2"
    assert bananahub._default_profile_for_provider("openai-compatible") == "gpt"


def test_doctor_reports_missing_secret_and_agent_contract():
    config = {"BANANAHUB_PROVIDER": "openai-compatible", "OPENAI_BASE_URL": "https://token.bigfish.space/v1"}
    resolved = {"BANANAHUB_PROVIDER": "test", "OPENAI_BASE_URL": "test"}
    bananahub._finalize_config(config, resolved)
    diagnosis = bananahub._diagnose_config_state(config, resolved_from=resolved)

    assert diagnosis["status"] == "needs_setup"
    assert diagnosis["provider"] == "openai-compatible"
    assert diagnosis["requires_user_secret"] is True
    assert diagnosis["active_api_key"]["config_key"] == "OPENAI_API_KEY"
    assert "api_key" in diagnosis["missing_fields"]
    assert "config quickset --provider openai-compatible" in diagnosis["suggested_commands"][0]
    assert "--api-key-stdin" in diagnosis["suggested_commands_stdin"][0]
    assert "gpt-image-2" in diagnosis["suggested_commands"][0]
    assert diagnosis["config_path"].endswith(".config/bananahub/config.json")
    assert "direct_agent_entry_when_user_explicitly_allows" in diagnosis["secret_entry_modes"]
    assert any("config quickset --api-key-stdin" in note for note in diagnosis["agent_notes"])
    assert any("interactive TTY" in note for note in diagnosis["agent_notes"])


def test_quickset_can_read_api_key_from_stdin():
    with TempHome() as config_path:
        old_stdin = sys.stdin
        try:
            sys.stdin = StringIO("stdin-key\n")
            args = quickset_args(api_key=None, api_key_stdin=True)
            stdout = StringIO()
            with redirect_stdout(stdout):
                bananahub.cmd_config_quickset(args)
        finally:
            sys.stdin = old_stdin

        raw = json.loads(config_path.read_text())

    assert raw["profiles"]["gpt"]["openai_api_key"] == "stdin-key"


def test_doctor_scopes_resolved_from_to_active_provider():
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

    diagnosis = bananahub._diagnose_config_state(config, resolved_from=resolved)

    assert diagnosis["resolved_from"]["api_key"] == "config.json"
    assert diagnosis["resolved_from"]["base_url"] is None
    assert diagnosis["ignored_config_sources"][0]["reason"] == "inactive for selected provider"


def test_doctor_reports_env_shadowed_by_persisted_profile():
    config = {
        "BANANAHUB_PROVIDER": "chatgpt-compatible",
        "BANANAHUB_TRANSPORT": "openai-rest",
        "BANANAHUB_AUTH_MODE": "api_key",
        "BANANAHUB_CHATGPT_API_KEY": "chat-key",
        "BANANAHUB_CHATGPT_BASE_URL": "https://token.bigfish.space",
        "BANANAHUB_MODEL": "gpt-5.4",
        "BANANAHUB_PROFILE": "chat",
    }
    resolved = {
        "BANANAHUB_PROVIDER": "config.json",
        "BANANAHUB_TRANSPORT": "default:chatgpt-compatible",
        "BANANAHUB_AUTH_MODE": "config.json",
        "BANANAHUB_CHATGPT_API_KEY": "config.json",
        "BANANAHUB_CHATGPT_BASE_URL": "config.json",
        "BANANAHUB_MODEL": "config.json",
        "BANANAHUB_PROFILE": "config.json",
    }
    skipped_env = [{
        "key": "BANANAHUB_CHATGPT_BASE_URL",
        "alias": "BANANAHUB_CHATGPT_BASE_URL",
        "source": "env:BANANAHUB_CHATGPT_BASE_URL",
        "active_source": "config.json",
        "reason": "persistent_config_precedence",
    }]

    diagnosis = bananahub._diagnose_config_state(config, resolved_from=resolved, skipped_env=skipped_env)

    assert diagnosis["status"] == "ok"
    assert diagnosis["precedence"]["env_mode"] == "fill-missing"
    assert diagnosis["effective_config"]["base_url"] == "https://token.bigfish.space"
    assert diagnosis["env_shadowed_config_sources"] == skipped_env
    assert any("BANANAHUB_ENV_OVERRIDE=1" in note for note in diagnosis["agent_notes"])


def test_dependency_status_is_provider_aware():
    openai_deps = bananahub._dependency_status_for_provider("openai-compatible")
    google_deps = bananahub._dependency_status_for_provider("google-ai-studio")

    assert "pillow" in openai_deps
    assert "google-genai" not in openai_deps
    assert "google-genai" in google_deps


def test_dependency_install_command_uses_current_python_user_site():
    command = bananahub._dependency_install_command(["pillow"])

    assert command[:4] == [sys.executable, "-m", "pip", "install"]
    assert "--user" in command
    assert command[-1] == "pillow"


def test_skill_layer_runtime_stub_is_machine_readable():
    stdout = StringIO()
    with redirect_stdout(stdout):
        handled = bananahub._handle_skill_layer_command(["optimize", "一只猫"])

    payload = json.loads(stdout.getvalue())

    assert handled is True
    assert payload["status"] == "skill_layer_command"
    assert payload["command"] == "optimize"
    assert "generate" in payload["runtime_commands"]


if __name__ == "__main__":
    test_quickset_openai_compatible_writes_gpt_profile()
    test_quickset_defaults_openai_compatible_to_gpt_image_2()
    test_doctor_reports_missing_secret_and_agent_contract()
    test_quickset_can_read_api_key_from_stdin()
    test_doctor_scopes_resolved_from_to_active_provider()
    test_doctor_reports_env_shadowed_by_persisted_profile()
    test_dependency_status_is_provider_aware()
    test_dependency_install_command_uses_current_python_user_site()
    test_skill_layer_runtime_stub_is_machine_readable()
    print("ok")
