from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Paths:
    repo_root: Path
    data_root: Path
    raw_root: Path
    normalized_root: Path
    reference_root: Path
    derived_root: Path
    published_root: Path
    status_dir: Path
    build_dir: Path
    manual_knmi_dir: Path


@dataclass(frozen=True)
class ModelConfig:
    n_values: tuple[int, ...]
    k_values: tuple[int, ...]
    d_values: tuple[int, ...]
    c_values: tuple[float, ...]
    lambda_decay: float


@dataclass(frozen=True)
class AppConfig:
    paths: Paths
    model: ModelConfig
    noaa_base_url: str
    knmi_base_url: str


def load_config() -> AppConfig:
    repo_root = Path(os.getenv("DATAPIPE_REPO_ROOT", Path.cwd())).resolve()
    data_root = repo_root / "data"
    published_root = data_root / "published"
    return AppConfig(
        paths=Paths(
            repo_root=repo_root,
            data_root=data_root,
            raw_root=data_root / "raw",
            normalized_root=data_root / "normalized",
            reference_root=data_root / "reference",
            derived_root=data_root / "derived",
            published_root=published_root,
            status_dir=published_root / "status",
            build_dir=repo_root / "build",
            manual_knmi_dir=repo_root / "manual" / "knmi",
        ),
        model=ModelConfig(
            n_values=tuple(range(2, 9)),
            k_values=(2, 3, 4),
            d_values=tuple(range(1, 8)),
            c_values=tuple(round(i / 10, 1) for i in range(11)),
            lambda_decay=float(os.getenv("DATAPIPE_LAMBDA_DECAY", "0.5")),
        ),
        noaa_base_url=os.getenv("NOAA_BASE_URL", "https://example.noaa.invalid/daily"),
        knmi_base_url=os.getenv("KNMI_BASE_URL", "https://example.knmi.invalid/daily"),
    )
