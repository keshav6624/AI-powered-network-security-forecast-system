"""
ORM models — PostgreSQL (or SQLite fallback)
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from app.database.base import Base


def utcnow():
    return datetime.now(timezone.utc)


class NetworkWindow(Base):
    __tablename__ = "network_windows"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, index=True)
    features = Column(JSON, nullable=False)
    label = Column(String(50), nullable=True)
    source_ip = Column(String(64), nullable=True)
    dest_ip = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, index=True)
    attack_probability = Column(Float, nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)
    forecast_horizon = Column(Integer, default=5)
    model_name = Column(String(100), nullable=True)
    anomaly_score = Column(Float, nullable=True)
    details = Column(JSON, nullable=True)  # per-model breakdown
    created_at = Column(DateTime(timezone=True), default=utcnow)


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, index=True)
    severity = Column(String(20), nullable=False, index=True)  # LOW|MEDIUM|HIGH|CRITICAL
    risk_score = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="active")  # active|acknowledged|resolved
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class Host(Base):
    __tablename__ = "hosts"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(64), unique=True, index=True)
    hostname = Column(String(128), nullable=True)
    status = Column(String(20), default="active")
    first_seen = Column(DateTime(timezone=True), default=utcnow)
    last_seen = Column(DateTime(timezone=True), default=utcnow)


class ModelRun(Base):
    __tablename__ = "model_runs"
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    started_at = Column(DateTime(timezone=True), default=utcnow)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="running")
    metrics = Column(JSON, nullable=True)
    artifact_path = Column(String(512), nullable=True)
