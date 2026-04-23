from __future__ import annotations


def combine_disturbance(weather: float, atmospheric: float, c: float) -> float:
    return (1.0 - c) * weather + c * atmospheric


def classify_c(c: float) -> tuple[str, str]:
    if c <= 0.2:
        return "weather_dominates", "blue"
    if c >= 0.8:
        return "atmospheric_dominates", "orange"
    return "hybrid", "purple"
