"""
NetGuard AI — FastAPI Application
SIH26153 — AI-Powered Network Attack Forecasting System
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.database.database import init_db
from app.api import api_router

setup_logging()
logger = get_logger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_startup", env=settings.app_env, demo=settings.demo_mode)
    # DB init (safe, creates tables if not exist)
    try:
        init_db()
    except Exception as e:
        logger.error("db_init_failed_startup", error=str(e))
    # Pre-load models (non-blocking on missing artifacts)
    try:
        from app.ml.model_loader import get_registry
        get_registry().load_all()
    except Exception as e:
        logger.error("model_registry_failed", error=str(e))
    # Pre-load replay windows
    try:
        from app.services.replay_engine import get_replay_engine
        get_replay_engine()
    except Exception as e:
        logger.error("replay_init_failed", error=str(e))
    logger.info("app_ready", port=settings.backend_port)
    yield
    logger.info("app_shutdown")

app = FastAPI(
    title="NetGuard AI — Network Attack Forecasting",
    description="Forecast future attack probability from temporal network behavior (SIH26153)",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "name": "NetGuard AI",
        "description": "AI-Powered Network Attack Forecasting System — SIH26153",
        "status": "ONLINE",
        "demo_mode": settings.demo_mode,
        "docs": "/docs",
        "health": "/api/health",
        "dashboard": "/api/dashboard",
    }
