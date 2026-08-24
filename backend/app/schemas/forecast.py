from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    timestamp: datetime
    attack_probability: float = Field(ge=0, le=1)
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    anomaly_score: Optional[float] = None


class ForecastHistoryResponse(BaseModel):
    points: List[ForecastPoint]
    horizon_minutes: int
    demo_mode: bool = False


class LatestForecastResponse(BaseModel):
    timestamp: datetime
    attack_probability: float
    risk_score: int
    risk_level: str
    horizon_minutes: int
    trend: str  # increasing | stable | decreasing
    demo_mode: bool = False
