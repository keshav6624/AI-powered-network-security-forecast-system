"""XGBoost predictor — tabular benchmark. Artifact: models/xgboost/xgboost_model.json"""
import numpy as np
from app.ml.predictors.base import BasePredictor
from app.core.config import get_settings
from app.core.logging import get_logger
from app.ml.model_loader import get_model_loader, ModelLoadError

logger = get_logger(__name__)


class XGBoostPredictor(BasePredictor):
    name = "xgboost"
    display_name = "XGBoost"

    def __init__(self):
        super().__init__()
        self.model = None

    def load(self) -> bool:
        settings = get_settings()
        if settings.demo_mode:
            self._available = True
            self._demo = True
            logger.info("xgboost_demo_mode")
            return True
        try:
            self.model = get_model_loader().load_xgboost()
            self._available = True
            self._demo = False
            logger.info("xgboost_loaded")
            return True
        except ModelLoadError as e:
            self._available = False
            self._load_error = str(e)
            logger.warning("xgboost_unavailable", error=str(e))
            return False

    def predict_proba(self, x: np.ndarray) -> float:
        if self._demo or self.model is None:
            from app.ml.demo_models import demo_xgboost
            return demo_xgboost(x)
        import xgboost as xgb
        dmat = xgb.DMatrix(x)
        return float(self.model.predict(dmat)[0])
