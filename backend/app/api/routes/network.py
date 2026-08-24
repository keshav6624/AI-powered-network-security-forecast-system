from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.dashboard_service import get_dashboard_data

router = APIRouter()

@router.get("/network/graph")
def network_graph(db: Session = Depends(get_db)):
    data = get_dashboard_data(db)
    return data["network_graph"]

@router.get("/network/hosts")
def network_hosts(db: Session = Depends(get_db)):
    from app.database.models import Host
    hosts = db.query(Host).limit(100).all()
    if not hosts:
        # demo fallback
        return [
            {"ip_address": "10.0.0.12", "hostname": "workstation-12", "status": "active"},
            {"ip_address": "10.0.0.47", "hostname": "workstation-47", "status": "suspicious"},
            {"ip_address": "10.0.0.98", "hostname": "db-server-01", "status": "active"},
            {"ip_address": "192.168.1.1", "hostname": "gateway", "status": "active"},
        ]
    return [{"ip_address": h.ip_address, "hostname": h.hostname, "status": h.status} for h in hosts]
