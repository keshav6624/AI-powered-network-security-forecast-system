"""Predictor registry built on top of artifact loading."""
from typing import TYPE_CHECKING

from app.core.logging import get_logger
from app.ml.model_loader import ModelLoader, get_model_loader

if TYPE_CHECKING:
    from app.ml.predictors.base import BasePredictor

logger = get_logger(__name__)


class ModelRegistry:
    """Construct predictors and expose their runtime status."""

    def __init__(self, loader: ModelLoader):
        self.loader = loader
        self.predictors: dict[str, BasePredictor] = {}
        self._load()

    @staticmethod
    def _predictor_types():
        from app.ml.predictors.isolation_forest import IsolationForestPredictor
        from app.ml.predictors.logistic import LogisticPredictor
        from app.ml.predictors.lstm import LSTMPredictor
        from app.ml.predictors.transformer import TransformerPredictor
        from app.ml.predictors.xgboost import XGBoostPredictor

        return {
            "logistic_regression": LogisticPredictor,
            "xgboost": XGBoostPredictor,
            "lstm": LSTMPredictor,
            "transformer": TransformerPredictor,
            "isolation_forest": IsolationForestPredictor,
        }

    def _load(self) -> None:
        artifact_status = self.loader.predict_status()
        predictor_types = self._predictor_types()
        for key, info in artifact_status.items():
            if not info["status"].startswith("Available"):
                continue
            predictor_type = predictor_types.get(key)
            if predictor_type is None:
                logger.warning("predictor_unknown", key=key)
                continue
            try:
                predictor = predictor_type()
                predictor.load()
                self.predictors[key] = predictor
            except Exception as error:
                logger.warning("predictor_load_failed", key=key, error=str(error))

    def load_all(self) -> dict[str, dict]:
        return {
            key: {
                "name": predictor.name,
                "available": predictor.is_available(),
                "demo": predictor.is_demo(),
            }
            for key, predictor in self.predictors.items()
        }

    def get(self, key: str):
        return self.predictors.get(key)

    def status_list(self) -> list[dict]:
        result = []
        for key, info in self.loader.predict_status().items():
            predictor = self.predictors.get(key)
            available = predictor.is_available() if predictor else False
            demo = predictor.is_demo() if predictor else False
            status = "Demo" if demo else "Available" if available else info["status"]
            result.append({
                "model": key,
                "display_name": info["name"],
                "status": status,
                "available": available,
                "demo": demo,
                "artifact_path": info["path"],
                "latency_ms": None,
            })
        return result


_registry: ModelRegistry | None = None


def get_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry(get_model_loader())
    return _registry


def reset_registry() -> None:
    global _registry
    _registry = None
