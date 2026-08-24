"""
Model loader — loads real trained artifacts (lazy, never crashes, clear errors).

File types:
  .joblib        → joblib.load
  .keras         → tensorflow.keras.models.load_model
  xgboost .json  → xgboost.Booster()
  .json          → json.load (metadata / feature columns)
  .csv           → pandas.read_csv

Preprocessing uses the SAME feature order (feature_columns.json) and
scaler (network_state_scaler.joblib) produced during Colab training.
NO retraining. NO refitting. NO renaming of artifacts.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from app.core.model_config import model_paths
from app.core.logging import get_logger

logger = get_logger(__name__)


class ModelLoadError(RuntimeError):
    pass


class ModelLoader:
    """Lazy loader for all trained artifacts."""

    def __init__(self):
        self.paths = model_paths()
        self._cache: dict = {}
        self._errors: dict = {}

    # ---------------- helpers ----------------
    def _require(self, key: str) -> Path:
        p = self.paths[key]
        if not p.exists():
            raise ModelLoadError(f"Artifact not found: {p}")
        return p

    # ---------------- model loading ----------------

    def load_logistic_regression(self):
        import joblib
        log = joblib.load(str(self._require("logistic_regression")))
        return log

    def load_xgboost(self):
        import xgboost as xgb
        b = xgb.Booster()
        b.load_model(str(self._require("xgboost")))
        return b

    def load_lstm(self):
        from tensorflow import keras
        m = keras.models.load_model(str(self._require("lstm")))
        return m

    def load_transformer(self):
        from tensorflow import keras
        m = keras.models.load_model(str(self._require("transformer")))
        return m

    def load_isolation_forest(self):
        import joblib
        iso = joblib.load(str(self._require("isolation_forest")))
        return iso

    def load_scaler(self):
        import joblib
        sc = joblib.load(str(self._require("scaler")))
        return sc

    def load_feature_columns(self):
        p = self._require("feature_columns")
        return json.loads(p.read_text(encoding="utf-8"))

    def load_metadata(self):
        p = self._require("metadata")
        return json.loads(p.read_text(encoding="utf-8"))

    # ---------------- status ----------------

    def predict_status(self) -> Dict[str, dict]:
        """Return status dict for each model key."""
        names = {
            "logistic_regression": ("logistic_regression", "Logistic Regression"),
            "xgboost": ("xgboost", "XGBoost"),
            "lstm": ("lstm", "LSTM"),
            "transformer": ("temporal_transformer", "Temporal Transformer"),
            "isolation_forest": ("isolation_forest", "Isolation Forest"),
        }
        result = {}
        for key, (artifact_key, disp) in names.items():
            try:
                p = self.paths[artifact_key]
                exists = p.exists()
                result[key] = {
                    "name": disp,
                    "status": "Available" if exists else "Not Installed",
                    "path": str(p),
                    "error": None if exists else f"Artifact missing: {p}",
                }
            except Exception as e:
                result[key] = {
                    "name": disp,
                    "status": "Error",
                    "path": str(self.paths.get(key, "?")),
                    "error": str(e),
                }
        return result

    def available_keys(self) -> List[str]:
        """Return keys whose models are available (not demo)."""
        status = self.predict_status()
        return [k for k, v in status.items() if v["status"] == "Available"]

    def load_all(self) -> Dict[str, object]:
        """Load all available models and return dict of model objects."""
        loaded = {}
        for key in self.available_keys():
            try:
                if key == "logistic_regression":
                    loaded[key] = self.load_logistic_regression()
                elif key == "xgboost":
                    loaded[key] = self.load_xgboost()
                elif key == "lstm":
                    loaded[key] = self.load_lstm()
                elif key == "transformer":
                    loaded[key] = self.load_transformer()
                elif key == "isolation_forest":
                    loaded[key] = self.load_isolation_forest()
            except Exception as e:
                logger.warning("load_failed", key=key, error=str(e))
        return loaded


_loader: Optional[ModelLoader] = None


def get_model_loader() -> ModelLoader:
    global _loader
    if _loader is None:
        _loader = ModelLoader()
    return _loader


def get_registry():
    """Backward-compatible registry accessor."""
    from app.ml.registry import get_registry as registry_accessor

    return registry_accessor()
