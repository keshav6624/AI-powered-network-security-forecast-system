# Architecture — NetGuard AI

## 1. Core Concept (Forecasting)

```
Raw network state (CICFlowMeter)
  → Feature selection & ordering (feature_config.json)
  → Scaling (scaler.pkl)
  → Temporal sequence (seq_len=10)
  → 5 predictors (logistic, xgboost on 1×F; lstm, transformer on 1×seq×F; isolation forest anomaly)
  → Ensemble (weighted, skip unavailable) → fused p(attack @ t+5)
  → RiskEngine (0-100, trend-aware)
  → AlertEngine (threshold → DB)
  → Dashboard + Replay
```

## 2. Backend Layers

- **API** (`api/routes/*`) — thin, Pydantic validation only, delegates to services.
- **Services** — business logic: `forecasting.py` (orchestrates), `risk_engine.py`, `alert_engine.py`, `replay_engine.py` (threaded), `dashboard_service.py` (aggregation).
- **ML** — `BasePredictor` interface, `model_loader.ModelRegistry` (lazy, never crashes on missing artifact), `preprocessor` (mirrors Colab), `ensemble`, `demo_models`.
- **Database** — SQLAlchemy 2, `models.py` (5 tables), `repositories.py` (no raw SQL in services), `database.py` (postgres with sqlite fallback).

## 3. Demo vs Production

- `core/config.Settings` (`pydantic-settings`) reads `.env`. `DEMO_MODE=true` → predictors return deterministic hash-based mocks, `status=Demo`. `false` → loads `models/**/*.pkl/pt`.
- `ModelRegistry.status_list()` drives `GET /api/models/status` and frontend badges.

## 4. Frontend

- Vite + React, Tailwind tokens matching backend risk levels. `services/api.js` (axios) + `utils/format.js` (riskColor). Components are pure presentational; `pages/Dashboard.jsx` polls `/api/dashboard` + `/api/replay/status` every 2s for SOC live feel. React Flow for topology, Recharts for temporal.

## 5. Data Flow — Replay

```
sample_windows.json → ReplayEngine.windows (800 sampled)
  → start() thread loop: step() → ForecastingService.predict(db) → history (200)
  → dashboard timeline + forecast card + alerts
```

## 6. Deployment

Docker Compose: `postgres` (healthcheck) → `backend` (uvicorn) → `frontend` (nginx). All config via `.env` + `MODEL_DIR`.

## 7. Why This Structure

- ML inference isolated from routes (swap artifacts without touching API).
- Preprocessor config-driven (same JSON as Colab → no training/serving skew).
- Ensemble configurable (weights in config, not hardcoded).
- DB fallback ensures `docker compose up` works even if postgres cold, and tests run without external deps.
