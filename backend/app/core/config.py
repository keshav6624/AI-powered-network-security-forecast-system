"""
NetGuard AI — Centralized Configuration
SIH26153

Environment-driven, lazy-safe. All thresholds/magic numbers come from here.
"""
import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    app_env: str = Field(default="development", alias="APP_ENV")
    demo_mode: bool = Field(default=True, alias="DEMO_MODE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    secret_key: str = Field(default="netguard-dev-secret-change-me", alias="SECRET_KEY")

    # Server
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:5173", alias="CORS_ORIGINS")

    # Database
    database_url: str = Field(
        default="postgresql://netguard:netguard_secret@localhost:5432/netguard",
        alias="DATABASE_URL",
    )

    # Models
    model_dir: Path = Field(default=Path("./models"), alias="MODEL_DIR")
    preprocessing_dir: Path = Field(default=Path("./models/preprocessing"), alias="PREPROCESSING_DIR")

    # ML
    sequence_length: int = Field(default=10, alias="SEQUENCE_LENGTH")
    forecast_horizon_minutes: int = Field(default=5, alias="FORECAST_HORIZON_MINUTES")
    risk_threshold_critical: int = Field(default=80, alias="RISK_THRESHOLD_CRITICAL")
    risk_threshold_high: int = Field(default=60, alias="RISK_THRESHOLD_HIGH")
    risk_threshold_medium: int = Field(default=30, alias="RISK_THRESHOLD_MEDIUM")
    alert_threshold: int = Field(default=60, alias="ALERT_THRESHOLD")

    # Replay
    replay_sample_path: Path = Field(default=Path("./data/sample"), alias="REPLAY_SAMPLE_PATH")
    replay_default_speed: str = Field(default="1x", alias="REPLAY_DEFAULT_SPEED")

    # Ensemble weights (must sum ~1.0; used only when >1 model available)
    ensemble_weights: dict = Field(default={
        "logistic_regression": 0.15,
        "xgboost": 0.20,
        "lstm": 0.30,
        "transformer": 0.35,
    })
    # Isolation Forest is anomaly detector, not in ensemble average — used as additive signal


    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_demo(self) -> bool:
        return self.demo_mode

    def model_paths(self) -> dict[str, Path]:
        """Resolved artifact paths — delegates to core.model_config."""
        from app.core.model_config import model_paths as _mp
        return _mp()


@lru_cache
def get_settings() -> Settings:
    return Settings()
