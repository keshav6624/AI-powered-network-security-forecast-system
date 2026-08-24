from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.dashboard_service import get_dashboard_data

router = APIRouter()

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    data = get_dashboard_data(db)
    # Convert timestamp to iso for JSON
    return {
        **data,
        "timestamp": data["timestamp"].isoformat(),
    }
