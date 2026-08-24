from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.forecasting import ForecastingService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/predictions", response_model=PredictionResponse)
def create_prediction(payload: PredictionRequest, db: Session = Depends(get_db)):
    """
    Forecast future attack probability from current + historical network state.
    Accepts single feature dict or optional sequence for temporal models.
    """
    if not payload.features or len(payload.features) == 0:
        raise HTTPException(status_code=422, detail="features must be non-empty dict")

    svc = ForecastingService()
    try:
        result = svc.predict(
            features=payload.features,
            sequence=payload.sequence,
            db=db,
            source_ip=payload.source_ip,
        )
        # Map to PredictionResponse
        return PredictionResponse(
            timestamp=result["timestamp"],
            forecast=result["forecast"],
            models=result["models"],
            anomaly=result["anomaly"],
            risk=result["risk"],
            explanations=result["explanations"],
            model_details=result["model_details"],
            demo_mode=result["demo_mode"],
        )
    except Exception as e:
        logger.error("prediction_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"prediction failed: {str(e)[:300]}")
