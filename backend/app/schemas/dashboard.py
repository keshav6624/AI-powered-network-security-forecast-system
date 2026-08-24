from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class KPIs(BaseModel):
    active_hosts: int
    network_flows: int
    anomalies: int
    current_risk: int = Field(ge=0, le=100)
    attack_probability: float = Field(ge=0, le=1)


class ModelStatusItem(BaseModel):
    model: str
    display_name: str
    status: str  # Available | Not Installed | Demo | Error
    available: bool
    demo: bool
    artifact_path: str
    latency_ms: Optional[float] = None


class ModelPerformance(BaseModel):
    model: str
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None
    roc_auc: Optional[float] = None
    pr_auc: Optional[float] = None
    false_positive_rate: Optional[float] = None
    inference_latency_ms: Optional[float] = None


class DashboardResponse(BaseModel):
    timestamp: datetime
    kpis: KPIs
    forecast: Dict[str, Any]
    risk_timeline: List[Dict[str, Any]]
    models_status: List[ModelStatusItem]
    recent_alerts: List[Dict[str, Any]]
    network_graph: Dict[str, Any]
    demo_mode: bool = False
    system_status: str = "ONLINE"
