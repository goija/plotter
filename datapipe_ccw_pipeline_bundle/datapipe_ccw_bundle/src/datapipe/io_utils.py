from __future__ import annotations

from pathlib import Path
import json
import pandas as pd


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict) -> Path:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_csv(path: Path, rows: list[dict]) -> Path:
    ensure_parent(path)
    pd.DataFrame(rows).to_csv(path, index=False)
    return path
