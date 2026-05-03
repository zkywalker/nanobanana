#!/usr/bin/env python3
import importlib.util
import json
import os
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
                "api_key": "test-key",
                "model": "gpt-image-2",
                "base_url": "https://token.bigfish.space/v1",
            }
        },
        "default_profile": "gpt",
    }


def test_quickset_defaults_openai_compatible_to_gpt_image_2():
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
    assert "api_key" in diagnosis["missing_fields"]
    assert "config quickset --provider openai-compatible" in diagnosis["suggested_commands"][0]
    assert "gpt-image-2" in diagnosis["suggested_commands"][0]


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


if __name__ == "__main__":
    test_quickset_openai_compatible_writes_gpt_profile()
    test_quickset_defaults_openai_compatible_to_gpt_image_2()
    test_doctor_reports_missing_secret_and_agent_contract()
    test_dependency_status_is_provider_aware()
    test_dependency_install_command_uses_current_python_user_site()
    print("ok")
