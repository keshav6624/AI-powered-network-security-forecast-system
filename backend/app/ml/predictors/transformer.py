"""Temporal Transformer predictor. Artifact: models/transformer/temporal_transformer.keras (seq_len=20, F=28)."""
import numpy as np
from app.ml.predictors.base import BasePredictor
from app.core.config import get_settings
from app.core.logging import get_logger
from app.ml.model_loader import get_model_loader, ModelLoadError

logger = get_logger(__name__)


class TransformerPredictor(BasePredictor):
    name = "transformer"
    display_name = "Temporal Transformer"

    def __init__(self):
        super().__init__()
        self.model = None

    def load(self) -> bool:
        settings = get_settings()
        if settings.demo_mode:
            self._available = True
            self._demo = True
            logger.info("transformer_demo_mode")
            return True
        try:
            self.model = get_model_loader().load_transformer()
            self._available = True
            self._demo = False
            logger.info("transformer_loaded", input_shape=str(getattr(self.model, "input_shape", None)))
            return True
        except ModelLoadError as e:
            self._available = False
            self._load_error = str(e)
            logger.warning("transformer_unavailable", error=str(e))
            return False

    def predict_proba(self, x: np.ndarray) -> float:
        if self._demo or self.model is None:
            from app.ml.demo_models import demo_transformer
            return demo_transformer(x)
        out = self.model.predict(x, verbose=0)
        out = np.asarray(out).ravel()
        if out.size == 1:
            return float(np.clip(out[0], 0, 1))
        return float(np.clip(out[1], 0, 1))
