from __future__ import annotations

from math import exp


def exp_weights(d: int, lambda_decay: float) -> list[float]:
    raw = [exp(-lambda_decay * i) for i in range(d)]
    total = sum(raw)
    return [x / total for x in raw]


def ewma_latest_first(values_latest_first: list[float], lambda_decay: float) -> float:
    weights = exp_weights(len(values_latest_first), lambda_decay)
    return sum(w * v for w, v in zip(weights, values_latest_first))
