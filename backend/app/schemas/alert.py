from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class AlertCreate(BaseModel):
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    risk_score: int = Field(ge=0, le=100)
    message: str
    source: Optional[str] = None


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    severity: str
    risk_score: int
    message: str
    status: str  # active | acknowledged | resolved
    source: Optional[str] = None
    created_at: datetime



class AlertListResponse(BaseModel):
    alerts: List[AlertOut]
    total: int


class AlertUpdate(BaseModel):
    status: str  # acknowledged | resolved
