"""
Pydantic schemas for /api/predictions
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class NetworkFeatures(BaseModel):
    """Single network window feature vector. Keys validated against preprocessor feature_config."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    flow_duration: Optional[float] = None
    tot_fwd_pkts: Optional[float] = None
    tot_bwd_pkts: Optional[float] = None
    totlen_fwd_pkts: Optional[float] = Field(default=None, alias="totlen_fwd_pkts")
    flow_byts_s: Optional[float] = None
    flow_pkts_s: Optional[float] = None
    fwd_pkts_s: Optional[float] = None
    bwd_pkts_s: Optional[float] = None
    pkt_len_mean: Optional[float] = None
    pkt_len_std: Optional[float] = None
    syn_flag_cnt: Optional[float] = None
    rst_flag_cnt: Optional[float] = None
    psh_flag_cnt: Optional[float] = None
    ack_flag_cnt: Optional[float] = None
    active_mean: Optional[float] = None
    idle_mean: Optional[float] = None



class PredictionRequest(BaseModel):
    timestamp: Optional[datetime] = None
    features: Dict[str, float] = Field(description="CICFlowMeter feature dict")
    sequence: Optional[List[Dict[str, float]]] = Field(default=None, description="Optional temporal sequence length seq_len")
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None


class ModelPrediction(BaseModel):
    model_name: str
    attack_probability: float = Field(ge=0, le=1)
    available: bool = True
    latency_ms: Optional[float] = None
    demo: bool = False


class RiskInfo(BaseModel):
    score: int = Field(ge=0, le=100)
    level: str  # LOW | MEDIUM | HIGH | CRITICAL


class ForecastInfo(BaseModel):
    attack_probability: float = Field(ge=0, le=1)
    horizon_minutes: int
    confidence: Optional[float] = None


class AnomalyInfo(BaseModel):
    score: float = Field(ge=0, le=1)
    is_anomaly: bool = False


class PredictionResponse(BaseModel):
    timestamp: datetime
    forecast: ForecastInfo
    models: Dict[str, float]  # name -> prob (only available models)
    anomaly: AnomalyInfo
    risk: RiskInfo
    explanations: List[str]
    model_details: List[ModelPrediction]
    demo_mode: bool = False


class BatchPredictionRequest(BaseModel):
    windows: List[PredictionRequest]
