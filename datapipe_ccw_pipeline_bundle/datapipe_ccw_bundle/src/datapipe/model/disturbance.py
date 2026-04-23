from __future__ import annotations

from pathlib import Path
import pandas as pd

from ..config import AppConfig
from ..debruijn.lyndon import de_bruijn_sequence, cycle_words


def build_daily_disturbance(date: str, cfg: AppConfig) -> list[Path]:
    outputs: list[Path] = []
    for n in cfg.model.n_values:
        for k in cfg.model.k_values:
            seq = de_bruijn_sequence(k, n)
            states = cycle_words(seq, n)
            rows = []
            for i, state in enumerate(states):
                weather = ((i % 10) / 10.0)
                atmospheric = (((i * 3) % 10) / 10.0)
                rows.append({
                    "date": date,
                    "n": n,
                    "k": k,
                    "state": state,
                    "dist_weather": weather,
                    "dist_atmospheric": atmospheric,
                })
            out_path = cfg.paths.derived_root / "disturbance" / date / f"n{n}_k{k}.csv"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(rows).to_csv(out_path, index=False)
            outputs.append(out_path)
    return outputs
