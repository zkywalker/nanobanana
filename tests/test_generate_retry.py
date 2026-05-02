#!/usr/bin/env python3
import argparse
import contextlib
import http.client
import importlib.util
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "bananahub.py"
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("bananahub", MODULE_PATH)
bananahub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bananahub)


class FakeImage:
    width = 64
    height = 64


def build_generate_args(**overrides):
    values = {
        "prompt": "Create a cute robot sticker.",
        "config": None,
        "provider": None,
        "model": "gpt-image-2",
        "aspect": "1:1",
        "image_size": None,
        "resize": None,
        "size": None,
        "output": "/tmp/bananahub-retry-test.png",
        "save_prompt": False,
        "prompt_output": None,
        "no_fallback": True,
        "openai_size": None,
        "quality": None,
        "background": None,
        "output_format": None,
        "output_compression": None,
        "template_id": None,
        "template_repo": None,
        "template_distribution": None,
        "template_source": None,
        "no_telemetry": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def run_generate_with_openai_attempts(attempts, args=None):
    config = {
        "BANANAHUB_PROVIDER": bananahub.PROVIDER_OPENAI_COMPATIBLE,
        "BANANAHUB_TRANSPORT": bananahub.TRANSPORT_OPENAI_REST,
        "GEMINI_API_KEY": "test-key",
        "OPENAI_BASE_URL": "https://token.bigfish.space/v1",
    }
    runtime_support = {
        "provider": bananahub.PROVIDER_OPENAI_COMPATIBLE,
        "transport": bananahub.TRANSPORT_OPENAI_REST,
        "capabilities": {"generate": True},
    }
    calls = []

    def fake_openai_try_generate(*call_args, **call_kwargs):
        calls.append({"args": call_args, "kwargs": call_kwargs})
        outcome = attempts[len(calls) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    originals = {
        "load_config": bananahub.load_config,
        "_runtime_support_status": bananahub._runtime_support_status,
        "_archive_prompt_for_command": bananahub._archive_prompt_for_command,
        "_openai_try_generate": bananahub._openai_try_generate,
        "_save_png_bytes": bananahub._save_png_bytes,
    }
    import time

    original_sleep = time.sleep
    bananahub.load_config = lambda config_file=None: dict(config)
    bananahub._runtime_support_status = lambda loaded_config: dict(runtime_support)
    bananahub._archive_prompt_for_command = lambda *call_args, **call_kwargs: None
    bananahub._openai_try_generate = fake_openai_try_generate
    bananahub._save_png_bytes = lambda image_bytes, output_path, resize_dims=None: FakeImage()
    time.sleep = lambda delay: None
    stdout = io.StringIO()
    exit_code = 0
    try:
        with contextlib.redirect_stdout(stdout):
            try:
                bananahub.cmd_generate(args or build_generate_args())
            except SystemExit as system_exit:
                exit_code = system_exit.code
    finally:
        bananahub.load_config = originals["load_config"]
        bananahub._runtime_support_status = originals["_runtime_support_status"]
        bananahub._archive_prompt_for_command = originals["_archive_prompt_for_command"]
        bananahub._openai_try_generate = originals["_openai_try_generate"]
        bananahub._save_png_bytes = originals["_save_png_bytes"]
        time.sleep = original_sleep

    output = stdout.getvalue().strip()
    payload = json.loads(output.splitlines()[-1]) if output else None
    return exit_code, payload, calls


def test_transient_network_error_retries_once_by_default_then_succeeds():
    exit_code, payload, calls = run_generate_with_openai_attempts(
        [
            RuntimeError("Network error: Remote end closed connection without response"),
            (b"fake-png", [], None),
        ],
    )

    assert exit_code == 0
    assert payload["status"] == "ok"
    assert payload["actual_model"] == "gpt-image-2"
    assert len(calls) == 2


def test_non_transient_auth_error_does_not_retry():
    exit_code, payload, calls = run_generate_with_openai_attempts(
        [RuntimeError("HTTP 401: invalid_api_key")]
    )

    assert exit_code == 1
    assert payload["status"] == "error"
    assert payload["error"] == "HTTP 401: invalid_api_key"
    assert len(calls) == 1
    assert payload["models_tried"] == [
        {"model": "gpt-image-2", "error": "HTTP 401: invalid_api_key"}
    ]


def test_server_error_detection_includes_transient_network_markers():
    retryable_errors = [
        http.client.RemoteDisconnected("Remote end closed connection without response"),
        RuntimeError("RemoteDisconnected: Remote end closed connection without response"),
        RuntimeError("Network error: Remote end closed connection without response"),
        RuntimeError("Connection reset by peer"),
        RuntimeError("Connection aborted during image generation"),
        TimeoutError("timed out"),
        RuntimeError("HTTP 503: overloaded"),
    ]
    non_retryable_errors = [
        RuntimeError("HTTP 401: invalid_api_key"),
        RuntimeError("HTTP 403: forbidden"),
        RuntimeError("Content policy violation"),
        RuntimeError("Safety blocked the prompt"),
    ]

    for retryable_error in retryable_errors:
        assert bananahub._is_server_error(retryable_error) is True
    for non_retryable_error in non_retryable_errors:
        assert bananahub._is_server_error(non_retryable_error) is False


if __name__ == "__main__":
    test_transient_network_error_retries_once_by_default_then_succeeds()
    test_non_transient_auth_error_does_not_retry()
    test_server_error_detection_includes_transient_network_markers()
    print("ok")
