from __future__ import annotations


def pseudo_recover_error(dist_value: float, n: int) -> float:
    return min(1.0, max(0.0, dist_value / max(1, n)))
