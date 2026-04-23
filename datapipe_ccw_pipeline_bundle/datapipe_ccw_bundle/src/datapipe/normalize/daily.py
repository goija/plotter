from __future__ import annotations

from pathlib import Path
import pandas as pd

from ..config import AppConfig


def normalize_day(date: str, cfg: AppConfig) -> list[Path]:
    out_dir = cfg.paths.normalized_root / date
    out_dir.mkdir(parents=True, exist_ok=True)
    weather = pd.DataFrame([
        {"date": date, "station_id": "NOAA_PLACEHOLDER", "metric": "weather_index", "value": 0.25, "quality_flag": "placeholder"}
    ])
    atmospheric = pd.DataFrame([
        {"date": date, "station_id": "ATM_PLACEHOLDER", "metric": "atmospheric_index", "value": 0.40, "quality_flag": "placeholder"}
    ])
    weather_path = out_dir / "weather.csv"
    atmospheric_path = out_dir / "atmospheric.csv"
    weather.to_csv(weather_path, index=False)
    atmospheric.to_csv(atmospheric_path, index=False)
    return [weather_path, atmospheric_path]
