"""IsolationForest — anomaly detector ONLY. Artifact: models/isolation_forest/isolation_forest.joblib."""
import numpy as np
from app.ml.predictors.base import BasePredictor
from app.core.config import get_settings
from app.core.logging import get_logger
from app.ml.model_loader import get_model_loader, ModelLoadError

logger = get_logger(__name__)


class IsolationForestPredictor(BasePredictor):
    name = "isolation_forest"
    display_name = "Isolation Forest"

    def __init__(self):
        super().__init__()
        self.model = None
        # Fit range for decision_function -> [0,1] from a real data slice
        self._norm_min = -0.5
        self._norm_max = 0.5
        self._norm_fitted = False

    def load(self) -> bool:
        settings = get_settings()
        if settings.demo_mode:
            self._available = True
            self._demo = True
            logger.info("isolation_forest_demo_mode")
            return True
        try:
            self.model = get_model_loader().load_isolation_forest()
            self._available = True
            self._demo = False
            logger.info("isolation_forest_loaded")
            return True
        except ModelLoadError as e:
            self._available = False
            self._load_error = str(e)
            logger.warning("isolation_forest_unavailable", error=str(e))
            return False

    def predict_proba(self, x: np.ndarray) -> float:
        """Return anomaly score in [0,1]. x is RAW (1, F)."""
        if self._demo or self.model is None:
            from app.ml.demo_models import demo_isolation_forest
            return demo_isolation_forest(x)
        return self.anomaly_score(x)

    def anomaly_score(self, x: np.ndarray) -> float:
        if self._demo or self.model is None:
            from app.ml.demo_models import demo_isolation_forest
            return demo_isolation_forest(x)
        df = float(self.model.decision_function(x)[0])
        # map decision_function (higher=normal) to anomaly score [0,1]
        # use exponential squashing calibrated on typical IF ranges
        score = 1.0 / (1.0 + np.exp(6.0 * df))
        return float(np.clip(score, 0.0, 1.0))
