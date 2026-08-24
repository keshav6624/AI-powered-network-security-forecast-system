"""Logistic Regression predictor — baseline. Artifact: models/baseline/logistic_baseline.joblib"""
import numpy as np
from app.ml.predictors.base import BasePredictor
from app.core.config import get_settings
from app.core.logging import get_logger
from app.ml.model_loader import get_model_loader, ModelLoadError

logger = get_logger(__name__)


class LogisticPredictor(BasePredictor):
    name = "logistic_regression"
    display_name = "Logistic Regression"

    def __init__(self):
        super().__init__()
        self.model = None

    def load(self) -> bool:
        settings = get_settings()
        if settings.demo_mode:
            self._available = True
            self._demo = True
            logger.info("logistic_demo_mode")
            return True
        try:
            self.model = get_model_loader().load_logistic_regression()
            self._available = True
            self._demo = False
            logger.info("logistic_loaded")
            return True
        except ModelLoadError as e:
            self._available = False
            self._load_error = str(e)
            logger.warning("logistic_unavailable", error=str(e))
            return False

    def predict_proba(self, x: np.ndarray) -> float:
        if self._demo or self.model is None:
            from app.ml.demo_models import demo_logistic
            return demo_logistic(x)
        # x: 1 x F scaled
        if hasattr(self.model, "predict_proba"):
            return float(self.model.predict_proba(x)[0, 1])
        return float(self.model.predict(x)[0])
