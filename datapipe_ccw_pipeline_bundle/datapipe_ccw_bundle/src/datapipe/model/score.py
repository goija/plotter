from __future__ import annotations

from pathlib import Path
import pandas as pd

from ..config import AppConfig
from .combined import combine_disturbance, classify_c
from .recover import pseudo_recover_error


def score_day(date: str, cfg: AppConfig) -> list[Path]:
    all_rows: list[dict] = []
    best_rows: list[dict] = []
    for n in cfg.model.n_values:
        for k in cfg.model.k_values:
            disturbance_path = cfg.paths.derived_root / "disturbance" / date / f"n{n}_k{k}.csv"
            df = pd.read_csv(disturbance_path)
            best_row: dict | None = None
            for d in cfg.model.d_values:
                for c in cfg.model.c_values:
                    combined = [combine_disturbance(w, a, c) for w, a in zip(df["dist_weather"], df["dist_atmospheric"])]
                    avg_combined = float(sum(combined) / len(combined))
                    error = pseudo_recover_error(avg_combined * (1 + 0.05 * (d - 1)), n)
                    case, color = classify_c(c)
                    row = {
                        "date": date,
                        "n": n,
                        "k": k,
                        "d": d,
                        "c": c,
                        "ccw": c,
                        "lambda": cfg.model.lambda_decay,
                        "error_combined": round(error, 6),
                        "dominance_case": case,
                        "color": color,
                        "weather_weight": round(1.0 - c, 3),
                        "atmospheric_weight": round(c, 3),
                    }
                    all_rows.append(row)
                    if best_row is None or row["error_combined"] < best_row["error_combined"]:
                        best_row = row
            assert best_row is not None
            best_rows.append({
                "date": date,
                "n": n,
                "k": k,
                "best_d": best_row["d"],
                "best_c": best_row["c"],
                "ccw": best_row["ccw"],
                "lambda": best_row["lambda"],
                "best_error": best_row["error_combined"],
                "dominance_case": best_row["dominance_case"],
                "color": best_row["color"],
                "weather_weight": best_row["weather_weight"],
                "atmospheric_weight": best_row["atmospheric_weight"],
            })
    full_path = cfg.paths.published_root / "scores" / "full_grid_scores.csv"
    best_path = cfg.paths.published_root / "scores" / "best_per_nk_combined.csv"
    full_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_rows).to_csv(full_path, index=False)
    pd.DataFrame(best_rows).to_csv(best_path, index=False)
    return [full_path, best_path]
