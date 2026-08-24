"""Database engine, session factory, and FastAPI dependency."""
import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.base import Base

logger = get_logger(__name__)
settings = get_settings()
DEFAULT_SQLITE_URL = "sqlite:///./netguard.db"


def _sqlite_engine(url: str) -> Engine:
    logger.info("using_sqlite", url=url)
    return create_engine(
        url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )


def create_database_engine(database_url: str | None = None) -> Engine:
    """Create an engine while preserving explicit SQLite database URLs."""
    url = database_url or settings.database_url
    if os.getenv("USE_SQLITE") == "1" and not url.startswith("sqlite"):
        url = DEFAULT_SQLITE_URL

    if url.startswith("sqlite"):
        return _sqlite_engine(url)

    try:
        import psycopg2  # noqa: F401

        engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={"connect_timeout": 2},
        )
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("postgres_connected", host=url.split("@")[-1] if "@" in url else url)
        return engine
    except Exception as error:
        if settings.app_env.lower() == "production":
            raise
        logger.warning("postgres_unreachable_fallback_sqlite_dev", error=str(error)[:200])
        return _sqlite_engine(DEFAULT_SQLITE_URL)


engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    database = SessionLocal()
    try:
        yield database
    except Exception:
        database.rollback()
        raise
    finally:
        database.close()


def init_db() -> None:
    """Create all application tables registered on the shared metadata base."""
    from app.database import models  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("database_initialized")
    except Exception as error:
        logger.error("database_init_failed", error=str(error))
        raise
