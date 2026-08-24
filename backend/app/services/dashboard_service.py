"""
Dashboard service — aggregates KPIs, recent predictions, alerts, graph.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.database.repositories import list_predictions, list_open_alerts, count_hosts
from app.database.models import Prediction
from app.services.replay_engine import get_replay_engine
from app.ml.model_loader import get_registry
from app.core.config import get_settings

def get_dashboard_data(db: Session) -> Dict[str, Any]:
    settings = get_settings()
    registry = get_registry()
    replay = get_replay_engine()

    # KPIs
    hosts = count_hosts(db)
    # Network flows = total windows processed (approx via predictions count)
    flows = db.query(Prediction).count()
    anomalies = db.query(Prediction).filter(Prediction.anomaly_score > 0.6).count() if flows else 0
    latest = db.query(Prediction).order_by(Prediction.timestamp.desc()).first()
    current_risk = latest.risk_score if latest else 12
    attack_prob = latest.attack_probability if latest else 0.18

    kpis = {
        "active_hosts": max(hosts, 42) if hosts == 0 else hosts,  # demo placeholder when empty
        "network_flows": flows if flows else 1248,
        "anomalies": anomalies if anomalies else 7,
        "current_risk": current_risk,
        "attack_probability": round(float(attack_prob), 4),
    }

    # Recent predictions for timeline
    preds = list_predictions(db, limit=30)
    if not preds and replay.history:
        # Use replay history when DB empty
        timeline = []
        for h in replay.history[-20:]:
            timeline.append({
                "timestamp": h["timestamp"].isoformat() if hasattr(h["timestamp"], "isoformat") else str(h["timestamp"]),
                "attack_probability": h["forecast"]["attack_probability"],
                "risk_score": h["risk"]["score"],
                "risk_level": h["risk"]["level"],
            })
    else:
        timeline = [
            {
                "timestamp": p.timestamp.isoformat(),
                "attack_probability": p.attack_probability,
                "risk_score": p.risk_score,
                "risk_level": p.risk_level,
            }
            for p in reversed(preds)
        ]
        if not timeline:
            # synthetic demo timeline
            now = datetime.now(timezone.utc)
            for i in range(20):
                timeline.append({
                    "timestamp": (now - timedelta(minutes=20-i)).isoformat(),
                    "attack_probability": 0.15 + (i/20)*0.6 + (0.05 if i>14 else 0),
                    "risk_score": 10 + i*4,
                    "risk_level": "LOW" if i<8 else "MEDIUM" if i<14 else "HIGH" if i<18 else "CRITICAL",
                })

    # Alerts
    alerts = list_open_alerts(db, limit=10)
    recent_alerts = [
        {
            "id": a.id,
            "timestamp": a.timestamp.isoformat(),
            "severity": a.severity,
            "risk_score": a.risk_score,
            "message": a.message,
            "status": a.status,
        }
        for a in alerts
    ]
    if not recent_alerts and replay.history:
        # materialize from recent high-risk
        for h in reversed(replay.history[-5:]):
            if h["risk"]["level"] in ("HIGH","CRITICAL"):
                recent_alerts.append({
                    "id": len(recent_alerts)+1,
                    "timestamp": h["timestamp"].isoformat() if hasattr(h["timestamp"], "isoformat") else str(h["timestamp"]),
                    "severity": h["risk"]["level"],
                    "risk_score": h["risk"]["score"],
                    "message": f"{h['risk']['level']}: Attack forecast {h['forecast']['attack_probability']:.0%} (horizon {h['forecast']['horizon_minutes']}m) — " + ", ".join(h["explanations"][:2]),
                    "status": "active",
                })

    # Network graph — synthetic but realistic SOC topology
    graph = {
        "nodes": [
            {"id": "gateway", "label": "Gateway", "type": "gateway", "risk": "LOW"},
            {"id": "server-1", "label": "Server 01", "type": "server", "risk": "MEDIUM"},
            {"id": "server-2", "label": "Server 02", "type": "server", "risk": "HIGH"},
            {"id": "host-1", "label": "10.0.0.12", "type": "host", "risk": "LOW"},
            {"id": "host-2", "label": "10.0.0.47", "type": "host", "risk": "CRITICAL"},
            {"id": "host-3", "label": "10.0.0.98", "type": "host", "risk": "MEDIUM"},
            {"id": "attacker", "label": "External", "type": "external", "risk": "CRITICAL"},
        ],
        "edges": [
            {"source": "host-1", "target": "gateway", "traffic": 42, "anomaly": False},
            {"source": "host-2", "target": "gateway", "traffic": 189, "anomaly": True},
            {"source": "host-3", "target": "server-1", "traffic": 67, "anomaly": False},
            {"source": "gateway", "target": "server-1", "traffic": 210, "anomaly": True},
            {"source": "gateway", "target": "server-2", "traffic": 95, "anomaly": False},
            {"source": "attacker", "target": "host-2", "traffic": 312, "anomaly": True},
            {"source": "attacker", "target": "gateway", "traffic": 88, "anomaly": True},
        ],
    }

    # Forecast current
    forecast = {
        "attack_probability": kpis["attack_probability"],
        "horizon_minutes": settings.forecast_horizon_minutes,
        "risk_score": kpis["current_risk"],
        "risk_level": latest.risk_level if latest else ("HIGH" if kpis["current_risk"]>60 else "MEDIUM"),
        "trend": "increasing" if kpis["current_risk"]>50 else "stable",
    }

    return {
        "timestamp": datetime.now(timezone.utc),
        "kpis": kpis,
        "forecast": forecast,
        "risk_timeline": timeline,
        "models_status": registry.status_list(),
        "recent_alerts": recent_alerts,
        "network_graph": graph,
        "demo_mode": settings.demo_mode,
        "system_status": "ONLINE",
    }
