#!/usr/bin/env python3
"""Nano Banana - Gemini image generation CLI tool."""

import argparse
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_env():
    """Load API config from ~/.gemini/.env"""
    env_path = Path.home() / ".gemini" / ".env"
    if not env_path.exists():
        print(json.dumps({"status": "error", "error": f"Config not found: {env_path}"}))
        sys.exit(1)

    config = {}
    for line in env_path.read_text().strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


def get_client(config):
    """Create Gemini client from config."""
    from google import genai

    api_key = config.get("GEMINI_API_KEY", "")
    base_url = config.get("GOOGLE_GEMINI_BASE_URL", "")

    if not api_key:
        print(json.dumps({"status": "error", "error": "GEMINI_API_KEY not set in ~/.gemini/.env"}))
        sys.exit(1)

    http_options = {"api_version": "v1beta"}
    if base_url:
        http_options["base_url"] = base_url

    return genai.Client(api_key=api_key, http_options=http_options)


def cmd_init(args):
    """Check environment readiness and guide user through setup."""
    checks = []
    env_path = Path.home() / ".gemini" / ".env"

    # 1. Check config file
    if env_path.exists():
        config = {}
        for line in env_path.read_text().strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

        checks.append({"name": "config_file", "ok": True, "path": str(env_path)})

        # 2. Check API key
        api_key = config.get("GEMINI_API_KEY", "")
        if api_key:
            masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            checks.append({"name": "api_key", "ok": True, "value": masked})
        else:
            checks.append({"name": "api_key", "ok": False, "error": "GEMINI_API_KEY not set"})

        # 3. Check base URL
        base_url = config.get("GOOGLE_GEMINI_BASE_URL", "")
        if base_url:
            checks.append({"name": "base_url", "ok": True, "value": base_url})
        else:
            checks.append({"name": "base_url", "ok": True, "value": "(default Google endpoint)"})
    else:
        checks.append({"name": "config_file", "ok": False, "error": f"Not found: {env_path}"})
        checks.append({"name": "api_key", "ok": False, "error": "Config file missing"})
        checks.append({"name": "base_url", "ok": False, "error": "Config file missing"})

    # 4. Check Python dependencies
    deps = {}
    for pkg, import_name in [("google-genai", "google.genai"), ("pillow", "PIL")]:
        try:
            __import__(import_name)
            deps[pkg] = True
        except ImportError:
            deps[pkg] = False
    checks.append({"name": "dependencies", "ok": all(deps.values()), "detail": deps})

    all_ok = all(c["ok"] for c in checks)

    # 5. API connectivity test (only if basic checks pass)
    if all_ok and not args.skip_test:
        try:
            config = load_env()
            client = get_client(config)
            response = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents="Say OK",
            )
            text = ""
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        text = part.text
                        break
            checks.append({"name": "api_test", "ok": True, "response": text[:100]})
        except Exception as e:
            checks.append({"name": "api_test", "ok": False, "error": str(e)[:200]})

    all_ok = all(c["ok"] for c in checks)

    setup_guide = None
    if not all_ok:
        setup_guide = {
            "steps": [
                "1. Create config directory: mkdir -p ~/.gemini",
                "2. Create ~/.gemini/.env with the following content:",
                "   GEMINI_API_KEY=your_api_key_here",
                "   GOOGLE_GEMINI_BASE_URL=https://generativelanguage.googleapis.com  (or your proxy URL)",
                "3. Get your API key from: https://aistudio.google.com/apikey",
                "4. Install dependencies: pip install google-genai pillow",
                "5. Run again: python3 nanobanana.py init",
            ]
        }

    print(json.dumps({
        "status": "ok" if all_ok else "incomplete",
        "checks": checks,
        "setup_guide": setup_guide,
    }, ensure_ascii=False, indent=2))

    if not all_ok:
        sys.exit(1)


def cmd_models(args):
    """List available image generation models."""
    models = [
        {"id": "gemini-3-pro-image-preview", "name": "Nano Banana Pro", "default": True},
        {"id": "gemini-2.0-flash-preview-image-generation", "name": "Nano Banana Flash", "default": False},
    ]
    print(json.dumps({"status": "ok", "models": models}, ensure_ascii=False))


def cmd_edit(args):
    """Edit an existing image based on a text prompt."""
    import io

    # Validate input image before importing heavy dependencies
    input_path = Path(args.input)
    if not input_path.exists():
        print(json.dumps({
            "status": "error",
            "error": f"Input image not found: {input_path}",
        }, ensure_ascii=False))
        sys.exit(1)

    from google.genai import types
    from PIL import Image

    try:
        input_image = Image.open(str(input_path))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": f"Cannot read input image: {e}",
        }, ensure_ascii=False))
        sys.exit(1)

    config_data = load_env()
    client = get_client(config_data)

    model = args.model or "gemini-3-pro-image-preview"
    prompt = args.prompt

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path.cwd()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"nanobanana_edit_{timestamp}.png"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        generate_config = types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        )

        response = client.models.generate_content(
            model=model,
            contents=[prompt, input_image],
            config=generate_config,
        )

        # Extract image and text from response
        if not response.candidates or not response.candidates[0].content.parts:
            print(json.dumps({
                "status": "error",
                "error": "No response generated. The model may have refused the prompt due to content policy.",
                "prompt": prompt,
                "model": model,
            }, ensure_ascii=False))
            sys.exit(1)

        image_part = None
        text_parts = []
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                image_part = part
            elif hasattr(part, "text") and part.text:
                text_parts.append(part.text)

        if not image_part:
            error_msg = "No image in response."
            if text_parts:
                error_msg += f" Model said: {' '.join(text_parts)}"
            print(json.dumps({
                "status": "error",
                "error": error_msg,
                "prompt": prompt,
                "model": model,
            }, ensure_ascii=False))
            sys.exit(1)

        # Save image
        image_data = image_part.inline_data.data
        image = Image.open(io.BytesIO(image_data))

        # Handle size parameter
        if args.size:
            try:
                w, h = map(int, args.size.split("x"))
                image = image.resize((w, h), Image.LANCZOS)
            except ValueError:
                pass

        image.save(str(output_path), "PNG")

        result = {
            "status": "ok",
            "file": str(output_path),
            "input": str(input_path),
            "model": model,
            "prompt": prompt,
            "image_size": f"{image.width}x{image.height}",
        }
        if text_parts:
            result["model_text"] = " ".join(text_parts)
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        error_msg = str(e)
        hint = ""
        if "SAFETY" in error_msg.upper() or "BLOCKED" in error_msg.upper():
            hint = "Content was blocked by safety filters. Try rephrasing the prompt."
        elif "QUOTA" in error_msg.upper() or "429" in error_msg:
            hint = "API quota exceeded. Wait a moment and try again."
        elif "401" in error_msg or "403" in error_msg:
            hint = "Authentication failed. Check GEMINI_API_KEY in ~/.gemini/.env"
        elif "TIMEOUT" in error_msg.upper() or "CONNECT" in error_msg.upper():
            hint = "Network error. Check your connection and base_url in ~/.gemini/.env"

        result = {
            "status": "error",
            "error": error_msg,
            "prompt": prompt,
            "model": model,
        }
        if hint:
            result["hint"] = hint
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)


def cmd_generate(args):
    """Generate an image from a text prompt."""
    from google.genai import types
    from PIL import Image
    import io

    config = load_env()
    client = get_client(config)

    model = args.model or "gemini-3-pro-image-preview"
    prompt = args.prompt
    aspect_ratio = args.aspect or "1:1"

    # Determine output path (default: current working directory)
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path.cwd()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"nanobanana_{timestamp}.png"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        generate_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
            ),
        )

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=generate_config,
        )

        # Extract image from response
        if not response.candidates or not response.candidates[0].content.parts:
            print(json.dumps({
                "status": "error",
                "error": "No image generated. The model may have refused the prompt due to content policy.",
                "prompt": prompt,
                "model": model,
            }, ensure_ascii=False))
            sys.exit(1)

        image_part = None
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                image_part = part
                break

        if not image_part:
            # Check if there's a text response instead
            text_parts = [p.text for p in response.candidates[0].content.parts if p.text]
            error_msg = "No image in response."
            if text_parts:
                error_msg += f" Model said: {' '.join(text_parts)}"
            print(json.dumps({
                "status": "error",
                "error": error_msg,
                "prompt": prompt,
                "model": model,
            }, ensure_ascii=False))
            sys.exit(1)

        # Save image
        image_data = image_part.inline_data.data
        image = Image.open(io.BytesIO(image_data))

        # Handle size parameter
        if args.size:
            try:
                w, h = map(int, args.size.split("x"))
                image = image.resize((w, h), Image.LANCZOS)
            except ValueError:
                pass

        image.save(str(output_path), "PNG")

        print(json.dumps({
            "status": "ok",
            "file": str(output_path),
            "model": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "image_size": f"{image.width}x{image.height}",
        }, ensure_ascii=False))

    except Exception as e:
        error_msg = str(e)
        hint = ""
        if "SAFETY" in error_msg.upper() or "BLOCKED" in error_msg.upper():
            hint = "Content was blocked by safety filters. Try rephrasing the prompt."
        elif "QUOTA" in error_msg.upper() or "429" in error_msg:
            hint = "API quota exceeded. Wait a moment and try again."
        elif "401" in error_msg or "403" in error_msg:
            hint = "Authentication failed. Check GEMINI_API_KEY in ~/.gemini/.env"
        elif "TIMEOUT" in error_msg.upper() or "CONNECT" in error_msg.upper():
            hint = "Network error. Check your connection and base_url in ~/.gemini/.env"

        result = {
            "status": "error",
            "error": error_msg,
            "prompt": prompt,
            "model": model,
        }
        if hint:
            result["hint"] = hint
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Nano Banana - Gemini image generation")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate an image from a prompt")
    gen_parser.add_argument("prompt", help="Text prompt for image generation")
    gen_parser.add_argument("--model", "-m", help="Model ID (default: gemini-3-pro-image-preview)")
    gen_parser.add_argument("--aspect", "-a", help="Aspect ratio, e.g. 1:1, 16:9, 9:16 (default: 1:1)")
    gen_parser.add_argument("--size", "-s", help="Resize output to WxH, e.g. 1024x1024")
    gen_parser.add_argument("--output", "-o", help="Output file path (default: current directory)")

    # edit command
    edit_parser = subparsers.add_parser("edit", help="Edit an existing image with a text prompt")
    edit_parser.add_argument("prompt", help="Text prompt describing the edit")
    edit_parser.add_argument("--input", "-i", required=True, help="Path to the source image")
    edit_parser.add_argument("--model", "-m", help="Model ID (default: gemini-3-pro-image-preview)")
    edit_parser.add_argument("--size", "-s", help="Resize output to WxH, e.g. 1024x1024")
    edit_parser.add_argument("--output", "-o", help="Output file path (default: current directory)")

    # models command
    subparsers.add_parser("models", help="List available models")

    # init command
    init_parser = subparsers.add_parser("init", help="Check environment and guide setup")
    init_parser.add_argument("--skip-test", action="store_true", help="Skip API connectivity test")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "edit":
        cmd_edit(args)
    elif args.command == "models":
        cmd_models(args)
    elif args.command == "init":
        cmd_init(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
