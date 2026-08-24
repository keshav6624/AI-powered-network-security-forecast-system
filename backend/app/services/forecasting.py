"""
Forecasting Service — orchestrates preprocessor → predictors → ensemble → risk.

Keeps business logic out of routes.
"""
from datetime import datetime, timezone
from typing import Dict, List, Optional
import numpy as np
from sqlalchemy.orm import Session

from app.ml.preprocessor import get_preprocessor
from app.ml.model_loader import get_registry
from app.ml.ensemble import fuse_predictions
from app.services.risk_engine import compute_risk
from app.services.alert_engine import maybe_create_alert
from app.ml.demo_models import demo_explanations
from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.repositories import create_prediction

logger = get_logger(__name__)


class ForecastingService:
    def __init__(self):
        self.registry = get_registry()
        self.preprocessor = get_preprocessor()
        self.settings = get_settings()

    def predict(
        self,
        features: Dict[str, float],
        sequence: Optional[List[Dict[str, float]]] = None,
        db: Optional[Session] = None,
        source_ip: Optional[str] = None,
        persist: bool = True,
    ) -> dict:
        """
        Main entry: returns dict matching PredictionResponse concept.
        Handles both single-window and temporal sequence paths.
        """
        now = datetime.now(timezone.utc)
        # Tabular models use raw features; temporal models use the saved scaler.
        single_vec = self.preprocessor.vector_raw(features)
        scaled_single_vec = self.preprocessor.vector_scaled(features)
        seq_full = [*(sequence or []), features]
        seq_vec = self.preprocessor.sequence_scaled(seq_full)

        model_probs: Dict[str, float] = {}
        model_details: List[dict] = []
        anomaly_score = 0.0

        # Tabular models: logistic, xgboost
        for name in ["logistic_regression", "xgboost"]:
            pred = self.registry.get(name)
            if not pred or not pred.is_available():
                continue
            model_input = scaled_single_vec if pred.is_demo() else single_vec
            prob, latency = pred.timed_proba(model_input)
            model_probs[name] = float(prob)
            model_details.append({
                "model_name": name,
                "attack_probability": float(prob),
                "available": True,
                "latency_ms": round(latency, 2),
                "demo": pred.is_demo(),
            })

        # Temporal models: lstm, transformer
        for name in ["lstm", "transformer"]:
            pred = self.registry.get(name)
            if not pred or not pred.is_available():
                continue
            prob, latency = pred.timed_proba(seq_vec)
            model_probs[name] = float(prob)
            model_details.append({
                "model_name": name,
                "attack_probability": float(prob),
                "available": True,
                "latency_ms": round(latency, 2),
                "demo": pred.is_demo(),
            })

        # Anomaly
        iso = self.registry.get("isolation_forest")
        if iso and iso.is_available():
            try:
                anomaly_input = scaled_single_vec if iso.is_demo() else single_vec
                anomaly_score, lat = iso.timed_proba(anomaly_input)
                anomaly_score = float(anomaly_score)
                model_details.append({
                    "model_name": "isolation_forest",
                    "attack_probability": anomaly_score,  # stored as score
                    "available": True,
                    "latency_ms": round(lat, 2),
                    "demo": iso.is_demo(),
                })
            except Exception:
                anomaly_score = float(np.clip(np.random.rand() * 0.3, 0, 1))
        else:
            # demo fallback already handled via is_available true in demo_mode
            anomaly_score = float(np.clip(np.mean(list(model_probs.values())) * 0.6 + 0.1 if model_probs else 0.2, 0, 1))

        # Fuse
        # Filter model_probs for forecast only (exclude isolation_forest already)
        fused_prob, confidence = fuse_predictions(model_probs)

        # Risk
        risk_score, risk_level = compute_risk(fused_prob, anomaly_score)

        # Explanations
        explanations = demo_explanations(features, fused_prob)

        # Build response
        result = {
            "timestamp": now,
            "forecast": {
                "attack_probability": round(fused_prob, 4),
                "horizon_minutes": self.settings.forecast_horizon_minutes,
                "confidence": round(confidence, 4),
            },
            "models": {k: round(v, 4) for k, v in model_probs.items()},
            "anomaly": {
                "score": round(anomaly_score, 4),
                "is_anomaly": anomaly_score > 0.6,
            },
            "risk": {
                "score": risk_score,
                "level": risk_level,
            },
            "explanations": explanations,
            "model_details": model_details,
            "demo_mode": self.settings.demo_mode,
        }

        # Persist + alert if db provided
        if db is not None and persist:
            try:
                # Make details JSON-serializable
                details_serializable = {
                    **result,
                    "timestamp": now.isoformat(),
                }
                create_prediction(
                    db,
                    timestamp=now,
                    attack_probability=float(fused_prob),
                    risk_score=int(risk_score),
                    risk_level=risk_level,
                    forecast_horizon=int(self.settings.forecast_horizon_minutes),
                    model_name="ensemble",
                    anomaly_score=float(anomaly_score),
                    details=details_serializable,
                )
                # alert
                maybe_create_alert(
                    db,
                    attack_prob=float(fused_prob),
                    anomaly_score=float(anomaly_score),
                    risk_score=int(risk_score),
                    risk_level=risk_level,
                    horizon=int(self.settings.forecast_horizon_minutes),
                    explanations=explanations,
                )
            except Exception as e:
                logger.warning("forecast_persist_failed", error=str(e))

        logger.info("forecast_done", prob=fused_prob, risk=risk_score, level=risk_level, demo=self.settings.demo_mode)
        return result
