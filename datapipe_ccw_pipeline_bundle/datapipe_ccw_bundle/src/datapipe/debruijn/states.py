from __future__ import annotations

from pathlib import Path
import pandas as pd

from ..config import AppConfig
from .lyndon import de_bruijn_sequence, as_word, cycle_words


def build_reference_states(cfg: AppConfig) -> list[Path]:
    outputs: list[Path] = []
    for n in cfg.model.n_values:
        for k in cfg.model.k_values:
            seq = de_bruijn_sequence(k, n)
            words = cycle_words(seq, n)
            out_dir = cfg.paths.reference_root / "debruijn" / f"n{n}_k{k}"
            out_dir.mkdir(parents=True, exist_ok=True)
            cycle_path = out_dir / "cycle.csv"
            states_path = out_dir / "states.csv"
            pd.DataFrame([{
                "n": n,
                "k": k,
                "cycle_type": "lyndon_fkm_lexleast",
                "cycle_string": as_word(seq),
                "cycle_length": len(seq),
            }]).to_csv(cycle_path, index=False)
            pd.DataFrame([
                {"state_index": i, "state_word": word, "next_state_index": (i + 1) % len(words)}
                for i, word in enumerate(words)
            ]).to_csv(states_path, index=False)
            outputs.extend([cycle_path, states_path])
    return outputs
