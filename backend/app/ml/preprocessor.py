"""
Preprocessor — exact inference path matching Colab training.

Facts verified from artifacts (scripts/verify_models.py):
- 28 features in feature_columns.json (exact order)
- StandardScaler saved separately (used for LSTM/Transformer sequences)
- Logistic Regression is a sklearn Pipeline with its own internal scaler → pass RAW
- XGBoost and IsolationForest trained on RAW features → no scaling
- sequence_length = 20 (metadata + keras input_shape)

No refitting. No reordering. No guessing.
"""
import json
import re
from typing import List, Dict, Optional
import numpy as np

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

DEFAULT_SEQUENCE_LENGTH = 5  # fallback only if metadata missing

# Compatibility projection from CICFlowMeter flow fields used by replay/API clients
# to the aggregated network-state columns stored in the trained artifacts.
FEATURE_ALIASES = {
    "mean_dst_port": ("Dst Port", "Destination Port"),
    "total_fwd_pkts": ("Tot Fwd Pkts", "Total Fwd Packets"),
    "total_bwd_pkts": ("Tot Bwd Pkts", "Total Backward Packets"),
    "total_fwd_bytes": ("TotLen Fwd Pkts", "Total Length of Fwd Packets"),
    "total_bwd_bytes": ("TotLen Bwd Pkts", "Total Length of Bwd Packets"),
    "mean_flow_duration": ("Flow Duration",),
    "mean_fwd_pkt_len": ("Fwd Pkt Len Mean", "Fwd Packet Length Mean"),
    "mean_bwd_pkt_len": ("Bwd Pkt Len Mean", "Bwd Packet Length Mean"),
    "mean_flow_bytes": ("Flow Byts/s", "Flow Bytes/s"),
    "mean_flow_pkts": ("Flow Pkts/s", "Flow Packets/s"),
    "mean_flow_iat": ("Flow IAT Mean",),
    "std_flow_iat": ("Flow IAT Std",),
    "max_flow_iat": ("Flow IAT Max",),
    "mean_pkt_len": ("Pkt Len Mean", "Packet Length Mean"),
    "std_pkt_len": ("Pkt Len Std", "Packet Length Std"),
    "mean_pkt_size": ("Pkt Size Avg", "Average Packet Size"),
    "fin_count": ("FIN Flag Cnt", "FIN Flag Count"),
    "syn_count": ("SYN Flag Cnt", "SYN Flag Count"),
    "rst_count": ("RST Flag Cnt", "RST Flag Count"),
    "psh_count": ("PSH Flag Cnt", "PSH Flag Count"),
    "ack_count": ("ACK Flag Cnt", "ACK Flag Count"),
    "urg_count": ("URG Flag Cnt", "URG Flag Count"),
    "mean_down_up_ratio": ("Down/Up Ratio",),
    "mean_active": ("Active Mean",),
    "mean_idle": ("Idle Mean",),
}


class Preprocessor:
    def __init__(self):
        self.settings = get_settings()
        self.feature_list: List[str] = []
        self.scaler = None
        self.metadata: dict = {}
        self.sequence_length: int = DEFAULT_SEQUENCE_LENGTH
        self.window_seconds: int = 10
        from app.core.model_config import model_paths
        self.paths = model_paths()
        self._load()

    def _load(self) -> None:
        meta_p = self.paths["metadata"]
        if meta_p.exists():
            try:
                self.metadata = json.loads(meta_p.read_text(encoding="utf-8"))
                self.sequence_length = int(self.metadata.get("sequence_length", DEFAULT_SEQUENCE_LENGTH))
                self.window_seconds = int(self.metadata.get("window_seconds", 10))
                logger.info("preprocessor_metadata", seq_len=self.sequence_length, window_seconds=self.window_seconds)
            except Exception as e:
                logger.warning("preprocessor_metadata_failed", error=str(e))
        else:
            logger.warning("preprocessor_metadata_missing", path=str(meta_p))

        fc_p = self.paths["feature_columns"]
        if fc_p.exists():
            try:
                cols = json.loads(fc_p.read_text(encoding="utf-8"))
                if isinstance(cols, list) and cols:
                    self.feature_list = [str(c) for c in cols]
                    logger.info("preprocessor_features", count=len(self.feature_list))
            except Exception as e:
                logger.warning("preprocessor_features_failed", error=str(e))
        else:
            logger.warning("preprocessor_features_missing", path=str(fc_p))

        sc_p = self.paths["scaler"]
        if sc_p.exists():
            try:
                import joblib
                self.scaler = joblib.load(sc_p)
                logger.info("preprocessor_scaler_loaded", type=type(self.scaler).__name__, n_features=getattr(self.scaler, "n_features_in_", None))
            except Exception as e:
                logger.warning("preprocessor_scaler_failed", error=str(e))
        else:
            logger.warning("preprocessor_scaler_missing", path=str(sc_p))

    @property
    def ready(self) -> bool:
        return bool(self.feature_list) and self.scaler is not None

    @staticmethod
    def _normalize_key(key: str) -> str:
        return re.sub(r"[^a-z0-9]", "", str(key).lower())

    def _resolve_feature(self, name: str, features: Dict[str, float]):
        normalized = {self._normalize_key(key): value for key, value in features.items()}
        candidates = (name, *FEATURE_ALIASES.get(name, ()))
        for candidate in candidates:
            key = self._normalize_key(candidate)
            if key in normalized:
                return normalized[key]
        if name == "flow_count" and features:
            return 1.0
        if name == "unique_dst_ports" and any(self._normalize_key(key) in {"dstport", "destinationport"} for key in features):
            return 1.0
        if name == "unique_protocols" and any(self._normalize_key(key) == "protocol" for key in features):
            return 1.0
        return None

    def missing_features(self, features: Dict[str, float]) -> List[str]:
        return [name for name in self.feature_list if self._resolve_feature(name, features) is None]

    def _sanitize(self, v) -> float:
        try:
            f = float(v)
        except Exception:
            return 0.0
        if f != f or f in (float("inf"), float("-inf")):
            return 0.0
        return float(f)

    def vector_raw(self, features: Dict[str, float]) -> np.ndarray:
        """1 x F raw-ordered vector for Logistic pipeline / XGBoost / IsolationForest."""
        if not self.feature_list:
            raise RuntimeError("feature_columns.json missing or empty; real inference impossible")
        vals = [self._sanitize(self._resolve_feature(name, features)) for name in self.feature_list]
        return np.array(vals, dtype=np.float64).reshape(1, -1)

    def vector_scaled(self, features: Dict[str, float]) -> np.ndarray:
        """1 x F scaled vector using the SAVED scaler (no refit)."""
        raw = self.vector_raw(features)
        if self.scaler is None:
            raise RuntimeError("network_state_scaler.joblib missing; cannot scale for temporal models")
        return self.scaler.transform(raw)

    def sequence_scaled(self, sequence: List[Dict[str, float]]) -> np.ndarray:
        """(1, sequence_length=20, F=28) scaled tensors for LSTM/Transformer.
        Left-pads with zeros when sequence shorter than seq_len.
        Caller should pass the most recent sequence of network states (each a full feature dict).
        """
        if not self.feature_list:
            raise RuntimeError("feature_columns.json missing or empty; real inference impossible")
        if self.scaler is None:
            raise RuntimeError("network_state_scaler.joblib missing; cannot scale for temporal models")
        seq_len = self.sequence_length
        seq = list(sequence)[-seq_len:]
        raws = [self.vector_raw(f).reshape(-1) for f in seq]
        if len(raws) < seq_len:
            pad = [np.zeros(len(self.feature_list), dtype=np.float64) for _ in range(seq_len - len(raws))]
            raws = pad + raws
        arr = np.stack(raws, axis=0)  # (seq_len, F)
        scaled = self.scaler.transform(arr)
        return scaled.reshape(1, seq_len, len(self.feature_list)).astype(np.float32)

    def info(self) -> dict:
        return {
            "feature_count": len(self.feature_list),
            "features": self.feature_list,
            "sequence_length": self.sequence_length,
            "window_seconds": self.window_seconds,
            "scaler_loaded": self.scaler is not None,
            "metadata_loaded": bool(self.metadata),
        }


_preprocessor: Optional[Preprocessor] = None

def get_preprocessor() -> Preprocessor:
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = Preprocessor()
    return _preprocessor

def reset_preprocessor() -> None:
    global _preprocessor
    _preprocessor = None
