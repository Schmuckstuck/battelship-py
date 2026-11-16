"""Helpers for writing replay data to disk."""

from __future__ import annotations

import json
from pathlib import Path

from .recorder import Recorder


def write_replay(destination: str | Path, recorder: Recorder) -> Path:
    """Serialize the recorder's rounds, stats and meta into a JSON file."""
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(recorder.to_serializable(), indent=2), encoding="utf-8")
    return path
