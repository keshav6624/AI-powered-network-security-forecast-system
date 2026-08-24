from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import list_alerts, update_alert_status
from app.schemas.alert import AlertListResponse, AlertOut, AlertUpdate

router = APIRouter()

@router.get("/alerts", response_model=AlertListResponse)
def get_alerts(
    limit: int = Query(default=50, ge=1, le=200),
    severity: str | None = None,
    db: Session = Depends(get_db),
):
    alerts = list_alerts(db, limit=limit, severity=severity)
    return AlertListResponse(
        alerts=[AlertOut.model_validate(a) for a in alerts],
        total=len(alerts),
    )

@router.patch("/alerts/{alert_id}")
def update_alert(alert_id: int, payload: AlertUpdate, db: Session = Depends(get_db)):
    if payload.status not in ("acknowledged", "resolved", "active"):
        raise HTTPException(status_code=422, detail="invalid status")
    updated = update_alert_status(db, alert_id, payload.status)
    if not updated:
        raise HTTPException(status_code=404, detail="alert not found")
    return AlertOut.model_validate(updated)

@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    updated = update_alert_status(db, alert_id, "acknowledged")
    if not updated:
        raise HTTPException(status_code=404, detail="alert not found")
    return AlertOut.model_validate(updated)

@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    updated = update_alert_status(db, alert_id, "resolved")
    if not updated:
        raise HTTPException(status_code=404, detail="alert not found")
    return AlertOut.model_validate(updated)
