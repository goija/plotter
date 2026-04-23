from __future__ import annotations

from pathlib import Path
import pandas as pd

from ..config import AppConfig


def publish_day(date: str, cfg: AppConfig) -> list[Path]:
    best_path = cfg.paths.published_root / "scores" / "best_per_nk_combined.csv"
    df = pd.read_csv(best_path)
    out_dir = cfg.paths.published_root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / f"summary_{date}.md"
    global_best = df.sort_values("best_error", ascending=True).iloc[0].to_dict()
    summary_path.write_text(
        "\n".join([
            f"# Daily summary {date}",
            "",
            f"Best n: {int(global_best['n'])}",
            f"Best k: {int(global_best['k'])}",
            f"Best d: {int(global_best['best_d'])}",
            f"Best c / ccw: {global_best['best_c']}",
            f"Dominance case: {global_best['dominance_case']}",
            f"Color (discrete reports): {global_best['color']}",
            "",
            "Use `ccw` for continuous image/graph color gradients.",
            "Red remains reserved for operational error conditions.",
        ]) + "\n",
        encoding="utf-8",
    )
    return [summary_path]
