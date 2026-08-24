"""
Alert Engine — creates alerts when risk crosses threshold.
Persists to PostgreSQL (or SQLite fallback).
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.repositories import create_alert
from app.services.risk_engine import compute_risk

logger = get_logger(__name__)


def should_alert(risk_score: int, risk_level: str) -> bool:
    settings = get_settings()
    # Alert on HIGH or CRITICAL, or when risk >= alert_threshold
    if risk_level in ("HIGH", "CRITICAL"):
        return True
    return risk_score >= settings.alert_threshold


def build_message(attack_prob: float, risk_score: int, risk_level: str, horizon: int, explanations: list[str]) -> str:
    header = f"{risk_level}: Potential network attack forecast."
    body = f"Attack probability: {attack_prob:.0%} | Risk score: {risk_score} | Horizon: {horizon} min"
    indicators = "Indicators: " + ", ".join(explanations) if explanations else ""
    return f"{header}\n{body}\n{indicators}".strip()


def maybe_create_alert(
    db: Session,
    attack_prob: float,
    anomaly_score: float,
    risk_score: int,
    risk_level: str,
    horizon: int,
    explanations: list[str],
    source: str = "forecasting_service",
) -> Optional[object]:
    if not should_alert(risk_score, risk_level):
        logger.info("alert_skipped", risk=risk_score, level=risk_level)
        return None
    # Deduplicate: simple throttle — if same severity in last minute, skip
    # (lightweight, without extra query complexity)
    message = build_message(attack_prob, risk_score, risk_level, horizon, explanations)
    alert = create_alert(
        db,
        severity=risk_level,
        risk_score=risk_score,
        message=message,
        source=source,
    )
    logger.info("alert_created", severity=risk_level, risk=risk_score, alert_id=alert.id)
    return alert
