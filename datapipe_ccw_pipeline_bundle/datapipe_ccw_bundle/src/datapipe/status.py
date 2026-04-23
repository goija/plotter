from __future__ import annotations

from pathlib import Path
from .io_utils import write_json


def write_status(path: Path, **payload: object) -> Path:
    return write_json(path, dict(payload))
