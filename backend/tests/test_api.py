"""Backend smoke tests — no trained models required (demo mode)."""
import os
os.environ["USE_SQLITE"] = "1"
os.environ["DEMO_MODE"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app
from app.database.database import init_db, SessionLocal
from app.database.models import Alert
from app.database.repositories import create_alert
init_db()

client = TestClient(app)

def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "ok"
    assert "demo_mode" in j

def test_dashboard():
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    j = r.json()
    assert "kpis" in j
    assert "forecast" in j
    assert "risk_timeline" in j
    assert len(j["models_status"]) == 5
    assert all(
        {"model", "display_name", "status", "available", "demo"} <= item.keys()
        for item in j["models_status"]
    )

def test_prediction():
    payload = {
        "features": {
            "Flow Duration": 120,
            "Tot Fwd Pkts": 10,
            "Flow Byts/s": 5000,
            "SYN Flag Cnt": 5,
            "Flow Pkts/s": 30,
            "Pkt Len Mean": 200,
            "Active Mean": 0.5,
            "Idle Mean": 0.1
        }
    }
    r = client.post("/api/predictions", json=payload)
    assert r.status_code == 200, r.text
    j = r.json()
    assert 0 <= j["forecast"]["attack_probability"] <= 1
    assert "risk" in j
    assert "explanations" in j

def test_demo_predictions_respond_to_feature_changes():
    quiet = client.post("/api/predictions", json={"features": {
        "Flow Duration": 100,
        "Tot Fwd Pkts": 2,
        "Flow Byts/s": 200,
        "Flow Pkts/s": 2,
        "SYN Flag Cnt": 0,
    }})
    suspicious = client.post("/api/predictions", json={"features": {
        "Flow Duration": 500000,
        "Tot Fwd Pkts": 500,
        "Flow Byts/s": 100000,
        "Flow Pkts/s": 1000,
        "SYN Flag Cnt": 200,
    }})
    assert quiet.status_code == 200, quiet.text
    assert suspicious.status_code == 200, suspicious.text
    quiet_models = quiet.json()["models"]
    suspicious_models = suspicious.json()["models"]
    assert any(
        abs(quiet_models[name] - suspicious_models[name]) > 0.001
        for name in quiet_models.keys() & suspicious_models.keys()
    )


def test_model_status():
    r = client.get("/api/models/status")
    assert r.status_code == 200
    j = r.json()
    assert "models" in j
    assert len(j["models"]) == 5

def test_replay_flow():
    r = client.get("/api/replay/status")
    assert r.status_code == 200
    r = client.post("/api/replay/step")
    assert r.status_code == 200, r.text
    assert "forecast" in r.json()
    r = client.post("/api/replay/speed", json={"speed":"5x"})
    assert r.status_code == 200

def test_alerts():
    r = client.get("/api/alerts")
    assert r.status_code == 200
    assert "alerts" in r.json()

def test_alert_actions_update_open_incident_queue():
    db = SessionLocal()
    alert = create_alert(
        db,
        severity="HIGH",
        risk_score=72,
        message="HIGH: Test incident",
        source="test",
    )
    alert_id = alert.id
    db.close()

    try:
        acknowledged = client.post(f"/api/alerts/{alert_id}/acknowledge")
        assert acknowledged.status_code == 200, acknowledged.text
        assert acknowledged.json()["status"] == "acknowledged"

        dashboard = client.get("/api/dashboard").json()
        queued = next(item for item in dashboard["recent_alerts"] if item["id"] == alert_id)
        assert queued["status"] == "acknowledged"

        resolved = client.post(f"/api/alerts/{alert_id}/resolve")
        assert resolved.status_code == 200, resolved.text
        assert resolved.json()["status"] == "resolved"

        dashboard = client.get("/api/dashboard").json()
        assert alert_id not in {item["id"] for item in dashboard["recent_alerts"]}
    finally:
        db = SessionLocal()
        db.query(Alert).filter(Alert.id == alert_id).delete()
        db.commit()
        db.close()


def test_forecast_latest():
    r = client.get("/api/forecasts/latest")
    assert r.status_code == 200
    assert "attack_probability" in r.json()
