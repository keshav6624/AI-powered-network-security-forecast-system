"""
Risk Engine — maps forecast prob + anomaly score + trend → risk 0–100 + level.

Thresholds configurable, not scientifically validated (as required).
"""
from typing import Tuple, Optional
import numpy as np
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def compute_risk(
    attack_prob: float,
    anomaly_score: float = 0.0,
    trend: Optional[str] = None,
    recent_probs: Optional[list[float]] = None,
) -> Tuple[int, str]:
    """
    Returns (risk_score 0-100, level)
    Formula (configurable conceptually):
      base = prob * 70
      anomaly_add = anomaly * 20
      trend_add = +10 if increasing else -5 if decreasing else 0
      risk = clamp(base + anomaly_add + trend_add)
    """
    settings = get_settings()
    base = float(attack_prob) * 70
    anomaly_add = float(anomaly_score) * 20

    # Trend from recent probs if not provided
    if trend is None and recent_probs and len(recent_probs) >= 3:
        # simple slope
        slope = recent_probs[-1] - recent_probs[0]
        if slope > 0.08:
            trend = "increasing"
        elif slope < -0.08:
            trend = "decreasing"
        else:
            trend = "stable"

    trend_add = 0
    if trend == "increasing":
        trend_add = 8
    elif trend == "decreasing":
        trend_add = -4

    raw = base + anomaly_add + trend_add
    # tiny non-linear boost for high prob
    if attack_prob > 0.85:
        raw += 5

    risk = int(np.clip(round(raw), 0, 100))

    # Level via thresholds
    if risk >= settings.risk_threshold_critical:
        level = "CRITICAL"
    elif risk >= settings.risk_threshold_high:
        level = "HIGH"
    elif risk >= settings.risk_threshold_medium:
        level = "MEDIUM"
    else:
        level = "LOW"

    logger.info("risk_computed", prob=attack_prob, anomaly=anomaly_score, trend=trend, risk=risk, level=level)
    return risk, level


def risk_color(level: str) -> str:
    return {
        "LOW": "#22c55e",
        "MEDIUM": "#eab308",
        "HIGH": "#f97316",
        "CRITICAL": "#ef4444",
    }.get(level, "#64748b")
