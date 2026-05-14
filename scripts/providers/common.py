"""Shared provider HTTP and image helpers."""

import json
import mimetypes
from pathlib import Path
from urllib import error as urlerror, request as urlrequest
from uuid import uuid4


def join_endpoint(base_url, path):
    """Join a configured base URL with a relative API path."""
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def extract_error_message_from_payload(payload, fallback):
    """Extract a concise error message from a JSON API error payload."""
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message") or error.get("code")
            if message:
                return str(message)
        if isinstance(error, str) and error.strip():
            return error.strip()
        message = payload.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    return fallback


def http_json_request(method, url, headers=None, payload=None, timeout=60):
    """Send a JSON HTTP request and parse the JSON response."""
    body = None
    request_headers = dict(headers or {})
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")

    req = urlrequest.Request(url, data=body, headers=request_headers, method=method.upper())
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            if not raw:
                return {}
            return json.loads(raw.decode("utf-8"))
    except urlerror.HTTPError as exc:
        raw = exc.read()
        fallback = f"{exc.code} {exc.reason}"
        if raw:
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                payload = None
            fallback = extract_error_message_from_payload(payload, fallback)
        raise RuntimeError(f"HTTP {exc.code}: {fallback}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def http_fetch_bytes(url, headers=None, timeout=60):
    """Fetch raw bytes from an HTTP endpoint."""
    req = urlrequest.Request(url, headers=headers or {}, method="GET")
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urlerror.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}: failed to fetch binary response") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc


def http_multipart_request(method, url, headers=None, fields=None, files=None, timeout=120):
    """Send a multipart/form-data request and parse JSON response."""
    boundary = f"----bananahub-{uuid4().hex}"
    body = bytearray()

    for name, value in (fields or {}).items():
        if value is None:
            continue
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")

    for item in files or []:
        field_name = item["field"]
        path = Path(item["path"])
        filename = path.name
        content_type = item.get("content_type") or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode("utf-8")
        )
        body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
        body.extend(path.read_bytes())
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))
    request_headers = dict(headers or {})
    request_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    req = urlrequest.Request(url, data=bytes(body), headers=request_headers, method=method.upper())
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            if not raw:
                return {}
            return json.loads(raw.decode("utf-8"))
    except urlerror.HTTPError as exc:
        raw = exc.read()
        fallback = f"{exc.code} {exc.reason}"
        if raw:
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                payload = None
            fallback = extract_error_message_from_payload(payload, fallback)
        raise RuntimeError(f"HTTP {exc.code}: {fallback}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc
