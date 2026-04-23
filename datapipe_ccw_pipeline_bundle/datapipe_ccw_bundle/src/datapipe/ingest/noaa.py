from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path

from ..config import AppConfig
from ..io_utils import write_json


@dataclass(frozen=True)
class StageResult:
    ok: bool
    message: str
    path: Path | None = None


def run_noaa(date: str, cfg: AppConfig) -> StageResult:
    target = cfg.paths.raw_root / "noaa" / date / "snapshot.json"
    payload = {
        "source": "noaa",
        "date": date,
        "fetched_at_utc": datetime.now(UTC).isoformat(),
        "status": "placeholder_success",
        "note": "Replace with real NOAA fetch/parser logic.",
    }
    write_json(target, payload)
    return StageResult(True, f"NOAA run completed for {date}", target)
