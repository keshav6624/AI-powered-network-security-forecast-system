"""
Lightweight repositories — keep DB access out of services/routes.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import Prediction, Alert, NetworkWindow, Host


# Predictions
def create_prediction(db: Session, **kwargs) -> Prediction:
    obj = Prediction(**kwargs)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_predictions(db: Session, limit: int = 100) -> List[Prediction]:
    return db.query(Prediction).order_by(Prediction.timestamp.desc()).limit(limit).all()


def latest_prediction(db: Session) -> Optional[Prediction]:
    return db.query(Prediction).order_by(Prediction.timestamp.desc()).first()


# Alerts
def create_alert(db: Session, severity: str, risk_score: int, message: str, source: str = "risk_engine") -> Alert:
    obj = Alert(severity=severity, risk_score=risk_score, message=message, source=source)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_alerts(db: Session, limit: int = 50, severity: Optional[str] = None) -> List[Alert]:
    q = db.query(Alert)
    if severity:
        q = q.filter(Alert.severity == severity)
    return q.order_by(Alert.timestamp.desc()).limit(limit).all()


def list_open_alerts(db: Session, limit: int = 50) -> List[Alert]:
    return (
        db.query(Alert)
        .filter(Alert.status != "resolved")
        .order_by(Alert.timestamp.desc())
        .limit(limit)
        .all()
    )


def update_alert_status(db: Session, alert_id: int, status: str) -> Optional[Alert]:
    obj = db.query(Alert).filter(Alert.id == alert_id).first()
    if not obj:
        return None
    obj.status = status
    db.commit()
    db.refresh(obj)
    return obj


# Hosts
def upsert_host(db: Session, ip_address: str) -> Host:
    host = db.query(Host).filter(Host.ip_address == ip_address).first()
    now = datetime.now(timezone.utc)
    if host:
        host.last_seen = now
    else:
        host = Host(ip_address=ip_address, last_seen=now, first_seen=now)
        db.add(host)
    db.commit()
    db.refresh(host)
    return host


def count_hosts(db: Session) -> int:
    return db.query(Host).count()


def recent_windows_count(db: Session, minutes: int = 60) -> int:
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    return db.query(NetworkWindow).filter(NetworkWindow.timestamp >= since).count()
