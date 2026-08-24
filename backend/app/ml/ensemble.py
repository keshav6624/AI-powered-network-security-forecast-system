"""
Ensemble — weighted fusion of forecast models + anomaly signal.

Does NOT blindly average: uses configurable weights, skips unavailable models,
and computes confidence from dispersion.
"""
from typing import Dict, Tuple, List
import numpy as np
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def fuse_predictions(model_probs: Dict[str, float], weights: Dict[str, float] | None = None) -> Tuple[float, float]:
    """
    Weighted average of available model probs.
    Returns (fused_prob, confidence)
    confidence = 1 - std(probs)  (higher agreement → higher confidence)
    """
    settings = get_settings()
    w = weights or settings.ensemble_weights
    if not model_probs:
        return 0.5, 0.0

    # Filter to forecast models only (exclude isolation_forest if accidentally included)
    filtered = {k: v for k, v in model_probs.items() if k != "isolation_forest"}
    if not filtered:
        filtered = model_probs

    # Normalize weights for available models
    available_weights = {k: w.get(k, 0.25) for k in filtered}
    total = sum(available_weights.values())
    if total == 0:
        # equal weight fallback
        total = len(filtered)
        available_weights = {k: 1.0 for k in filtered}
    # weighted sum
    fused = sum(filtered[k] * (available_weights[k] / total) for k in filtered)
    # confidence: 1 - std
    vals = list(filtered.values())
    std = float(np.std(vals)) if len(vals) > 1 else 0.0
    confidence = float(np.clip(1 - std * 2, 0, 1))  # scale std
    logger.info("ensemble_fused", fused=fused, confidence=confidence, models=list(filtered.keys()))
    return float(np.clip(fused, 0, 1)), confidence
