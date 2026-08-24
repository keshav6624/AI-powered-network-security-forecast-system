"""
Model artifact paths — derived from central Settings.model_dir.
No absolute Windows paths here; environment or project-relative only.
"""
from pathlib import Path
from app.core.config import get_settings


def model_paths() -> dict[str, Path]:
    """All artifact paths relative to settings.model_dir (env MODEL_DIR)."""
    m = Path(get_settings().model_dir)
    if not m.is_absolute():
        # resolve from project root (backend/../) when relative
        project_root = Path(__file__).resolve().parents[3]
        m = (project_root / m).resolve()
    return {
        "logistic_regression": m / "baseline" / "logistic_baseline.joblib",
        "xgboost": m / "xgboost" / "xgboost_model.json",
        "lstm": m / "lstm" / "lstm_world_model.keras",
        "temporal_transformer": m / "transformer" / "temporal_transformer.keras",
        "isolation_forest": m / "isolation_forest" / "isolation_forest.joblib",
        # preprocessing
        "feature_columns": m / "preprocessing" / "feature_columns.json",
        "scaler": m / "preprocessing" / "network_state_scaler.joblib",
        # metadata / data
        "metadata": m / "metadata" / "model_metadata.json",
        "model_comparison": m / "metadata" / "model_comparison.csv",
        "network_states": m / "data" / "network_states.csv",
        "registry": m / "model_registry.json",
    }
