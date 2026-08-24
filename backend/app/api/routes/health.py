from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database.database import get_db
from app.core.config import get_settings
from app.ml.model_loader import get_registry
from sqlalchemy import text

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    settings = get_settings()
    registry = get_registry()

    # DB check
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)[:100]}"

    models = registry.status_list()
    available_count = sum(1 for m in models if m["available"])

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": "ONLINE",
        "demo_mode": settings.demo_mode,
        "database": db_status,
        "models": {
            "total": len(models),
            "available": available_count,
            "details": models,
        },
        "version": "0.1.0",
        "forecast_horizon_minutes": settings.forecast_horizon_minutes,
    }
