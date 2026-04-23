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


def create_manual_knmi_helper(date: str, cfg: AppConfig, note: str) -> Path:
    target = cfg.paths.manual_knmi_dir / date / "manual_knmi_fetch.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        f"#!/usr/bin/env python3\n"
        f"\"\"\"Manual KNMI fetch helper for {date}.\"\"\"\n\n"
        f"print('Manual KNMI retrieval required for {date}')\n"
        f"print('Reason: {note}')\n"
        f"print('TODO: Replace placeholder URL/authentication with real KNMI download logic.')\n",
        encoding="utf-8",
    )
    return target


def run_knmi(date: str, cfg: AppConfig, manual_fallback: bool = True) -> StageResult:
    note = "KNMI automated source returned no usable rows for the target date yet"
    status_path = cfg.paths.raw_root / "knmi" / date / "status.json"
    write_json(status_path, {
        "source": "knmi",
        "date": date,
        "fetched_at_utc": datetime.now(UTC).isoformat(),
        "status": "manual_required",
        "note": note,
    })
    helper = create_manual_knmi_helper(date, cfg, note) if manual_fallback else None
    return StageResult(False, note, helper)
