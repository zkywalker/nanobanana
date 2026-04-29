#!/usr/bin/env python3
"""Validate BananaHub template metadata for v1/v2 compatibility."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOTS = [ROOT / "references" / "templates"]
MODEL_REGISTRY = ROOT / "references" / "model-registry.json"
VALID_TYPES = {"prompt", "workflow"}
VALID_QUALITIES = {"best", "good", "ok", "untested"}


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n([\s\S]*?)\r?\n---", text)
    if not match:
        return None, text
    return parse_simple_yaml(match.group(1)), text


def coerce(value):
    value = value.strip()
    if not value:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    return value


def parse_inline_list(value):
    if not (value.startswith("[") and value.endswith("]")):
        return None
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [coerce(part.strip()) for part in inner.split(",")]


def parse_simple_yaml(raw):
    result = {}
    lines = raw.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        match = re.match(r"^(\w[\w_]*):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        if value:
            inline = parse_inline_list(value)
            result[key] = inline if inline is not None else coerce(value)
            index += 1
            continue

        items = []
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].startswith("  - "):
            first = lines[cursor][4:].strip()
            obj = {}
            field = re.match(r"^(\w[\w_]*):\s*(.*)$", first)
            if field:
                obj[field.group(1)] = coerce(field.group(2))
                cursor += 1
                while cursor < len(lines) and lines[cursor].startswith("    "):
                    if lines[cursor].startswith("      "):
                        cursor += 1
                        continue
                    nested = re.match(r"^    (\w[\w_]*):\s*(.*)$", lines[cursor])
                    if nested:
                        nested_key = nested.group(1)
                        nested_value = nested.group(2).strip()
                        if nested_value:
                            inline = parse_inline_list(nested_value)
                            obj[nested_key] = inline if inline is not None else coerce(nested_value)
                            cursor += 1
                            continue
                        nested_items = []
                        cursor += 1
                        while cursor < len(lines) and lines[cursor].startswith("      - "):
                            nested_first = lines[cursor][8:].strip()
                            nested_obj = {}
                            nested_field = re.match(r"^(\w[\w_]*):\s*(.*)$", nested_first)
                            if nested_field:
                                nested_obj[nested_field.group(1)] = coerce(nested_field.group(2))
                                cursor += 1
                                while cursor < len(lines) and lines[cursor].startswith("        "):
                                    nested_attr = re.match(r"^        (\w[\w_]*):\s*(.*)$", lines[cursor])
                                    if nested_attr:
                                        attr_value = nested_attr.group(2).strip()
                                        inline = parse_inline_list(attr_value)
                                        nested_obj[nested_attr.group(1)] = inline if inline is not None else coerce(attr_value)
                                    cursor += 1
                                nested_items.append(nested_obj)
                            else:
                                nested_items.append(coerce(nested_first))
                                cursor += 1
                        obj[nested_key] = nested_items
                        continue
                    cursor += 1
                items.append(obj)
            else:
                items.append(coerce(first))
                cursor += 1
        result[key] = items
        index = cursor
    return result


def load_registry():
    if not MODEL_REGISTRY.exists():
        return {}, {}
    data = json.loads(MODEL_REGISTRY.read_text(encoding="utf-8"))
    return data.get("providers", {}), data.get("models", {})


def validate_template(path, providers, models):
    errors = []
    warnings = []
    fm, body = parse_frontmatter(path)
    if fm is None:
        return ["missing frontmatter"], warnings

    for key in ["title", "title_en", "author", "version", "profile", "aspect", "tags", "difficulty"]:
        if not fm.get(key):
            errors.append(f"missing required field: {key}")

    template_type = fm.get("type", "prompt")
    if template_type not in VALID_TYPES:
        errors.append(f"invalid type: {template_type}")

    tags = fm.get("tags")
    if not isinstance(tags, list) or len(tags) < 3:
        errors.append("tags must contain at least 3 entries")

    legacy_models = fm.get("models")
    provider_matrix = fm.get("providers")
    if not legacy_models and not provider_matrix:
        errors.append("missing models/providers compatibility metadata")

    if provider_matrix:
        if not isinstance(provider_matrix, list):
            errors.append("providers must be a list")
        else:
            for provider in provider_matrix:
                provider_id = provider.get("id") if isinstance(provider, dict) else None
                if not provider_id:
                    errors.append("provider entry missing id")
                    continue
                if providers and provider_id not in providers:
                    warnings.append(f"provider not found in registry: {provider_id}")
                model_entries = provider.get("models", [])
                if not isinstance(model_entries, list) or not model_entries:
                    errors.append(f"provider {provider_id} must list at least one model")
                    continue
                for model in model_entries:
                    model_id = model.get("id") if isinstance(model, dict) else None
                    if not model_id:
                        errors.append(f"provider {provider_id} has model without id")
                        continue
                    quality = model.get("quality", "untested")
                    if quality not in VALID_QUALITIES:
                        errors.append(f"model {model_id} has invalid quality: {quality}")
                    if models and model_id not in models:
                        warnings.append(f"model not found in registry: {model_id}")

    prompt_variants = fm.get("prompt_variants")
    if prompt_variants and not isinstance(prompt_variants, dict):
        warnings.append("prompt_variants parser only supports object form; check YAML formatting")

    samples = fm.get("samples", [])
    if samples and isinstance(samples, list):
        for sample in samples:
            if not isinstance(sample, dict):
                continue
            if sample.get("provider") and not sample.get("model"):
                errors.append(f"sample {sample.get('file', '<unknown>')} has provider but no model")
            if sample.get("file"):
                sample_path = path.parent / sample["file"]
                if not sample_path.exists():
                    warnings.append(f"sample file missing: {sample['file']}")

    if template_type == "prompt" and "## Prompt Template" not in body:
        errors.append("prompt template missing ## Prompt Template section")
    if template_type == "workflow" and "## Steps" not in body:
        errors.append("workflow template missing ## Steps section")
    return errors, warnings


def iter_templates(paths):
    for root in paths:
        if not root.exists():
            continue
        yield from sorted(root.glob("*/template.md"))


def main():
    paths = [Path(arg) for arg in sys.argv[1:]] if len(sys.argv) > 1 else TEMPLATE_ROOTS
    providers, models = load_registry()
    failed = False
    checked = 0
    for template in iter_templates(paths):
        checked += 1
        errors, warnings = validate_template(template, providers, models)
        try:
            rel = template.resolve().relative_to(ROOT)
        except ValueError:
            rel = template
        for warning in warnings:
            print(f"WARN {rel}: {warning}")
        for error in errors:
            failed = True
            print(f"ERROR {rel}: {error}")
    print(f"checked {checked} template(s)")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
