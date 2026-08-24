"""LSTM predictor — temporal forecaster. Artifact: models/lstm/lstm_world_model.keras (seq_len=20, F=28 from metadata)."""
import numpy as np
from app.ml.predictors.base import BasePredictor
from app.core.config import get_settings
from app.core.logging import get_logger
from app.ml.model_loader import get_model_loader, ModelLoadError

logger = get_logger(__name__)


class LSTMPredictor(BasePredictor):
    name = "lstm"
    display_name = "LSTM"

    def __init__(self):
        super().__init__()
        self.model = None

    def load(self) -> bool:
        settings = get_settings()
        if settings.demo_mode:
            self._available = True
            self._demo = True
            logger.info("lstm_demo_mode")
            return True
        try:
            self.model = get_model_loader().load_lstm()
            self._available = True
            self._demo = False
            logger.info("lstm_loaded", input_shape=str(getattr(self.model, "input_shape", None)))
            return True
        except ModelLoadError as e:
            self._available = False
            self._load_error = str(e)
            logger.warning("lstm_unavailable", error=str(e))
            return False

    def predict_proba(self, x: np.ndarray) -> float:
        # x expected (1, seq_len, F) already preprocessed
        if self._demo or self.model is None:
            from app.ml.demo_models import demo_lstm
            return demo_lstm(x)
        out = self.model.predict(x, verbose=0)
        out = np.asarray(out).ravel()
        if out.size == 1:
            return float(np.clip(out[0], 0, 1))
        return float(np.clip(out[1], 0, 1))
