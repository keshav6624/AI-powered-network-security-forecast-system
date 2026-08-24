from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database.database import get_db
from app.database.repositories import list_predictions
from app.core.config import get_settings
from app.services.replay_engine import get_replay_engine

router = APIRouter()

@router.get("/forecasts/latest")
def latest_forecast(db: Session = Depends(get_db)):
    settings = get_settings()
    replay = get_replay_engine()
    preds = list_predictions(db, limit=1)
    if preds:
        p = preds[0]
        return {
            "timestamp": p.timestamp.isoformat(),
            "attack_probability": p.attack_probability,
            "risk_score": p.risk_score,
            "risk_level": p.risk_level,
            "horizon_minutes": p.forecast_horizon,
            "anomaly_score": p.anomaly_score,
            "demo_mode": settings.demo_mode,
        }
    # fallback to replay history
    if replay.history:
        h = replay.history[-1]
        return {
            "timestamp": h["timestamp"].isoformat() if hasattr(h["timestamp"], "isoformat") else str(h["timestamp"]),
            "attack_probability": h["forecast"]["attack_probability"],
            "risk_score": h["risk"]["score"],
            "risk_level": h["risk"]["level"],
            "horizon_minutes": h["forecast"]["horizon_minutes"],
            "anomaly_score": h["anomaly"]["score"],
            "demo_mode": settings.demo_mode,
        }
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attack_probability": 0.18,
        "risk_score": 22,
        "risk_level": "LOW",
        "horizon_minutes": settings.forecast_horizon_minutes,
        "anomaly_score": 0.15,
        "demo_mode": settings.demo_mode,
    }

@router.get("/forecasts/history")
def forecast_history(limit: int = 50, db: Session = Depends(get_db)):
    settings = get_settings()
    preds = list_predictions(db, limit=limit)
    if preds:
        return {
            "points": [
                {
                    "timestamp": p.timestamp.isoformat(),
                    "attack_probability": p.attack_probability,
                    "risk_score": p.risk_score,
                    "risk_level": p.risk_level,
                    "anomaly_score": p.anomaly_score,
                }
                for p in reversed(preds)
            ],
            "horizon_minutes": settings.forecast_horizon_minutes,
            "demo_mode": settings.demo_mode,
        }
    # demo fallback
    replay = get_replay_engine()
    if replay.history:
        return {
            "points": [
                {
                    "timestamp": h["timestamp"].isoformat() if hasattr(h["timestamp"], "isoformat") else str(h["timestamp"]),
                    "attack_probability": h["forecast"]["attack_probability"],
                    "risk_score": h["risk"]["score"],
                    "risk_level": h["risk"]["level"],
                    "anomaly_score": h["anomaly"]["score"],
                }
                for h in replay.history[-limit:]
            ],
            "horizon_minutes": settings.forecast_horizon_minutes,
            "demo_mode": settings.demo_mode,
        }
    return {"points": [], "horizon_minutes": settings.forecast_horizon_minutes, "demo_mode": settings.demo_mode}
