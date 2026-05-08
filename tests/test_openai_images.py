#!/usr/bin/env python3
import base64
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

spec = importlib.util.spec_from_file_location(
    "providers.openai_images", ROOT / "scripts" / "providers" / "openai_images.py"
)
openai_images = importlib.util.module_from_spec(spec)
spec.loader.exec_module(openai_images)


def test_build_generation_payload_maps_image_size_and_options():
    payload, warnings = openai_images.build_generation_payload(
        "gpt-image-2",
        "a clean product photo",
        "1:1",
        native_image_size="2K",
        quality="high",
        background="transparent",
        output_format="png",
        output_compression=80,
    )

    assert warnings == []
    assert payload == {
        "model": "gpt-image-2",
        "prompt": "a clean product photo",
        "size": "2048x2048",
        "quality": "high",
        "background": "transparent",
        "output_format": "png",
        "output_compression": 80,
    }


def test_build_generation_payload_prefers_explicit_openai_size_for_compatible_gateway():
    payload, warnings = openai_images.build_generation_payload(
        "gpt-image-2",
        "wide banner",
        "16:9",
        native_image_size="4K",
        openai_size="1536x1024",
        provider="openai-compatible",
    )

    assert payload["size"] == "1536x1024"
    assert payload["extra_body"] == {"google": {"aspect_ratio": "16:9"}}
    assert warnings == [
        "`--image-size 4K` is ignored for openai-compatible generation when aspect ratio is not 1:1."
    ]


def test_build_generation_payload_for_gpt_image_omits_response_format_and_keeps_n():
    payload, warnings = openai_images.build_generation_payload(
        "gpt-image-2",
        "a matched icon set",
        "1:1",
        openai_size="1024x1024",
        n=3,
        moderation="low",
        user="user-123",
        provider="openai",
    )

    assert warnings == []
    assert payload == {
        "model": "gpt-image-2",
        "prompt": "a matched icon set",
        "size": "1024x1024",
        "n": 3,
        "moderation": "low",
        "user": "user-123",
    }
    assert "response_format" not in payload
    assert "extra_body" not in payload


def test_try_generate_posts_to_images_generations():
    calls = []
    image_bytes = b"fake-png"
    encoded = base64.b64encode(image_bytes).decode("ascii")

    def fake_http_json_request(method, url, headers, payload=None, timeout=None):
        calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "payload": payload,
                "timeout": timeout,
            }
        )
        return {"data": [{"b64_json": encoded}]}

    original = openai_images.http_json_request
    openai_images.http_json_request = fake_http_json_request
    try:
        result, warnings, error = openai_images.try_generate(
            {"BANANAHUB_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
            "gpt-image-2",
            "draw a precise icon",
            "1:1",
            openai_images.resolve_openai_endpoint_for_test,
            openai_size="1024x1024",
        )
    finally:
        openai_images.http_json_request = original

    assert result == [image_bytes]
    assert warnings == []
    assert error is None
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == "https://api.openai.com/v1/images/generations"
    assert calls[0]["headers"]["Authorization"] == "Bearer test-key"
    assert calls[0]["payload"]["size"] == "1024x1024"
    assert calls[0]["timeout"] == 120


def test_try_generate_openai_compatible_uses_gateway_safe_defaults():
    calls = []
    image_bytes = b"fake-png"
    encoded = base64.b64encode(image_bytes).decode("ascii")

    def fake_http_json_request(method, url, headers, payload=None, timeout=None):
        calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "payload": payload,
                "timeout": timeout,
            }
        )
        return {"data": [{"b64_json": encoded}]}

    original = openai_images.http_json_request
    openai_images.http_json_request = fake_http_json_request
    try:
        result, warnings, error = openai_images.try_generate(
            {
                "BANANAHUB_PROVIDER": "openai-compatible",
                "GEMINI_API_KEY": "test-key",
                "OPENAI_BASE_URL": "https://token.bigfish.space/v1",
            },
            "gpt-image-2",
            "Create a tiny cute robot sticker on a plain white background.",
            "1:1",
            openai_images.resolve_openai_endpoint_for_test,
        )
    finally:
        openai_images.http_json_request = original

    assert result == [image_bytes]
    assert warnings == []
    assert error is None
    assert calls[0]["url"] == "https://token.bigfish.space/v1/images/generations"
    assert calls[0]["headers"]["Authorization"] == "Bearer test-key"
    assert calls[0]["payload"] == {
        "model": "gpt-image-2",
        "prompt": "Create a tiny cute robot sticker on a plain white background.",
        "size": "auto",
        "quality": "medium",
        "output_format": "png",
    }
    assert "response_format" not in calls[0]["payload"]


def test_try_generate_openai_compatible_preserves_explicit_size():
    calls = []
    image_bytes = b"fake-png"
    encoded = base64.b64encode(image_bytes).decode("ascii")

    def fake_http_json_request(method, url, headers, payload=None, timeout=None):
        calls.append({"payload": payload})
        return {"data": [{"b64_json": encoded}]}

    original = openai_images.http_json_request
    openai_images.http_json_request = fake_http_json_request
    try:
        result, warnings, error = openai_images.try_generate(
            {
                "BANANAHUB_PROVIDER": "openai-compatible",
                "GEMINI_API_KEY": "test-key",
                "OPENAI_BASE_URL": "https://token.bigfish.space/v1",
            },
            "gpt-image-2",
            "Create a tiny cute robot sticker on a plain white background.",
            "1:1",
            openai_images.resolve_openai_endpoint_for_test,
            openai_size="1024x1024",
        )
    finally:
        openai_images.http_json_request = original

    assert result == [image_bytes]
    assert warnings == []
    assert error is None
    assert calls[0]["payload"]["size"] == "1024x1024"
    assert calls[0]["payload"]["quality"] == "medium"
    assert calls[0]["payload"]["output_format"] == "png"
    assert "response_format" not in calls[0]["payload"]


def test_try_generate_openai_compatible_preserves_explicit_quality_and_format():
    calls = []
    image_bytes = b"fake-png"
    encoded = base64.b64encode(image_bytes).decode("ascii")

    def fake_http_json_request(method, url, headers, payload=None, timeout=None):
        calls.append({"payload": payload})
        return {"data": [{"b64_json": encoded}]}

    original = openai_images.http_json_request
    openai_images.http_json_request = fake_http_json_request
    try:
        result, warnings, error = openai_images.try_generate(
            {
                "BANANAHUB_PROVIDER": "openai-compatible",
                "GEMINI_API_KEY": "test-key",
                "OPENAI_BASE_URL": "https://token.bigfish.space/v1",
            },
            "gpt-image-2",
            "Create a tiny cute robot sticker on a plain white background.",
            "1:1",
            openai_images.resolve_openai_endpoint_for_test,
            quality="high",
            output_format="webp",
        )
    finally:
        openai_images.http_json_request = original

    assert result == [image_bytes]
    assert warnings == []
    assert error is None
    assert calls[0]["payload"]["size"] == "auto"
    assert calls[0]["payload"]["quality"] == "high"
    assert calls[0]["payload"]["output_format"] == "webp"
    assert "response_format" not in calls[0]["payload"]


def test_try_generate_returns_multiple_images():
    calls = []
    images = [b"first", b"second"]
    encoded = [base64.b64encode(item).decode("ascii") for item in images]

    def fake_http_json_request(method, url, headers, payload=None, timeout=None):
        calls.append({"payload": payload})
        return {"data": [{"b64_json": encoded[0]}, {"b64_json": encoded[1]}]}

    original = openai_images.http_json_request
    openai_images.http_json_request = fake_http_json_request
    try:
        result, warnings, error = openai_images.try_generate(
            {"BANANAHUB_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
            "gpt-image-2",
            "draw two variants",
            "1:1",
            openai_images.resolve_openai_endpoint_for_test,
            n=2,
        )
    finally:
        openai_images.http_json_request = original

    assert result == images
    assert warnings == []
    assert error is None
    assert calls[0]["payload"]["n"] == 2


def test_try_edit_posts_multipart_with_mask_and_refs():
    calls = []
    image_bytes = b"edited"
    encoded = base64.b64encode(image_bytes).decode("ascii")

    def fake_http_multipart_request(method, url, headers, fields, files, timeout=None):
        calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "fields": fields,
                "files": files,
                "timeout": timeout,
            }
        )
        return {"data": [{"b64_json": encoded}]}

    original = openai_images.http_multipart_request
    openai_images.http_multipart_request = fake_http_multipart_request
    try:
        result, warnings, error = openai_images.try_edit(
            {"BANANAHUB_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
            "gpt-image-2",
            "replace background",
            "input.png",
            openai_images.resolve_openai_endpoint_for_test,
            ref_paths=["ref.png"],
            mask_path="mask.png",
            size="1024x1024",
            quality="high",
            output_format="webp",
            output_compression=70,
            n=2,
            moderation="low",
            user="user-123",
        )
    finally:
        openai_images.http_multipart_request = original

    assert result == [image_bytes]
    assert warnings == []
    assert error is None
    assert calls[0]["url"] == "https://api.openai.com/v1/images/edits"
    assert calls[0]["fields"] == {
        "model": "gpt-image-2",
        "prompt": "replace background",
        "size": "1024x1024",
        "quality": "high",
        "output_format": "webp",
        "output_compression": 70,
        "n": 2,
        "moderation": "low",
        "user": "user-123",
    }
    assert calls[0]["files"] == [
        {"field": "image[]", "path": "input.png"},
        {"field": "image[]", "path": "ref.png"},
        {"field": "mask", "path": "mask.png"},
    ]


def test_try_edit_single_image_uses_plain_image_field_and_legacy_response_format():
    calls = []
    image_bytes = b"edited"
    encoded = base64.b64encode(image_bytes).decode("ascii")

    def fake_http_multipart_request(method, url, headers, fields, files, timeout=None):
        calls.append({"fields": fields, "files": files})
        return {"data": [{"b64_json": encoded}]}

    original = openai_images.http_multipart_request
    openai_images.http_multipart_request = fake_http_multipart_request
    try:
        result, warnings, error = openai_images.try_edit(
            {"BANANAHUB_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
            "dall-e-2",
            "replace background",
            "input.png",
            openai_images.resolve_openai_endpoint_for_test,
        )
    finally:
        openai_images.http_multipart_request = original

    assert result == [image_bytes]
    assert warnings == []
    assert error is None
    assert calls[0]["fields"]["response_format"] == "b64_json"
    assert calls[0]["files"] == [{"field": "image", "path": "input.png"}]


def resolve_openai_endpoint_for_test(base_url):
    return {"configured_base_url": base_url, "resolved_base_url": base_url, "warnings": []}


openai_images.resolve_openai_endpoint_for_test = resolve_openai_endpoint_for_test


if __name__ == "__main__":
    test_build_generation_payload_maps_image_size_and_options()
    test_build_generation_payload_prefers_explicit_openai_size_for_compatible_gateway()
    test_build_generation_payload_for_gpt_image_omits_response_format_and_keeps_n()
    test_try_generate_posts_to_images_generations()
    test_try_generate_openai_compatible_uses_gateway_safe_defaults()
    test_try_generate_openai_compatible_preserves_explicit_size()
    test_try_generate_openai_compatible_preserves_explicit_quality_and_format()
    test_try_generate_returns_multiple_images()
    test_try_edit_posts_multipart_with_mask_and_refs()
    test_try_edit_single_image_uses_plain_image_field_and_legacy_response_format()
    print("ok")
