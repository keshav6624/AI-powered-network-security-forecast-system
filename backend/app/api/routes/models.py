from fastapi import APIRouter
from pathlib import Path
import json
from app.ml.model_loader import get_registry
from app.core.config import get_settings

router = APIRouter()

@router.get("/models/status")
def models_status():
    registry = get_registry()
    return {
        "models": registry.status_list(),
        "demo_mode": get_settings().demo_mode,
    }

@router.get("/models/performance")
def models_performance():
    """
    Loads from experiments/metrics.json or returns empty with explanation.
    Never fabricates.
    """
    candidates = [
        Path("experiments/metrics.json"),
        Path("experiments/results.json"),
        Path("./experiments/metrics.json"),
    ]
    for p in candidates:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                return {"available": True, "data": data, "source": str(p)}
            except Exception:
                pass
    # Check per-model config.json for metrics
    registry = get_registry()
    # Return honest empty
    return {
        "available": False,
        "message": "Model performance metrics not yet available. Train in Colab and place results in experiments/metrics.json",
        "models": registry.status_list(),
        "expected_path": "experiments/metrics.json",
        "metrics_schema": {
            "model": "string",
            "precision": "float",
            "recall": "float",
            "f1": "float",
            "roc_auc": "float",
            "pr_auc": "float",
            "false_positive_rate": "float",
            "inference_latency_ms": "float",
        },
    }
