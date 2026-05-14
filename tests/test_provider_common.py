#!/usr/bin/env python3
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("providers.common", ROOT / "scripts" / "providers" / "common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps({"ok": True}).encode("utf-8")


def test_multipart_request_does_not_force_accept_header(tmp_path=None):
    if tmp_path is None:
        import tempfile

        tmp_dir = tempfile.TemporaryDirectory()
        file_path = Path(tmp_dir.name) / "input.png"
    else:
        tmp_dir = None
        file_path = tmp_path / "input.png"
    file_path.write_bytes(b"fake")
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["headers"] = dict(req.header_items())
        captured["timeout"] = timeout
        return FakeResponse()

    original = common.urlrequest.urlopen
    common.urlrequest.urlopen = fake_urlopen
    try:
        result = common.http_multipart_request(
            "POST",
            "https://example.com/upload",
            headers={"Authorization": "Bearer test"},
            fields={"model": "gpt-image-2"},
            files=[{"field": "image", "path": file_path}],
            timeout=900,
        )
    finally:
        common.urlrequest.urlopen = original
        if tmp_dir is not None:
            tmp_dir.cleanup()

    assert result == {"ok": True}
    assert captured["timeout"] == 900
    assert "Accept" not in captured["headers"]
    assert captured["headers"]["Authorization"] == "Bearer test"
    assert captured["headers"]["Content-type"].startswith("multipart/form-data; boundary=")


if __name__ == "__main__":
    test_multipart_request_does_not_force_accept_header()
    print("ok")
