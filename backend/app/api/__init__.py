from fastapi import APIRouter
from app.api.routes import health, predictions, forecasts, alerts, dashboard, network, models, replay

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router, tags=["health"])
api_router.include_router(predictions.router, tags=["predictions"])
api_router.include_router(forecasts.router, tags=["forecasts"])
api_router.include_router(alerts.router, tags=["alerts"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(network.router, tags=["network"])
api_router.include_router(models.router, tags=["models"])
api_router.include_router(replay.router, tags=["replay"])
