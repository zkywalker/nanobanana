#!/usr/bin/env python3
"""BananaHub compatibility launcher for the legacy nanobanana script."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("nanobanana.py")), run_name="__main__")
