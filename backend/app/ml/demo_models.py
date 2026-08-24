"""
Deterministic demo predictors — used when DEMO_MODE=true or artifacts missing.
All outputs are deterministic from input hash, so replay is reproducible.
"""
import hashlib
import numpy as np


def _seed_from_array(x: np.ndarray) -> int:
    h = hashlib.md5(x.tobytes()).hexdigest()
    return int(h[:8], 16) % (2**31)


def demo_logistic(x: np.ndarray) -> float:
    """Baseline demo: logistic-like sigmoid on summed scaled features."""
    seed = _seed_from_array(x)
    rng = np.random.default_rng(seed)
    # Use mean of x as signal
    sig = float(np.mean(x))
    # inject small deterministic noise
    base = 1 / (1 + np.exp(- (sig * 2.5 - 0.5)))
    jitter = rng.uniform(-0.07, 0.07)
    return float(np.clip(base + jitter, 0.02, 0.97))


def demo_xgboost(x: np.ndarray) -> float:
    seed = _seed_from_array(x) ^ 0x9E3779B9
    rng = np.random.default_rng(seed)
    sig = float(np.mean(x) * 1.1 + np.std(x) * 0.3)
    base = 1 / (1 + np.exp(- (sig * 2.2 - 0.3)))
    jitter = rng.uniform(-0.06, 0.06)
    return float(np.clip(base + jitter, 0.02, 0.97))


def demo_lstm(x: np.ndarray) -> float:
    """Expects (1, seq, F) or (1,F). Use temporal coherence: last frame heavier."""
    if x.ndim == 3:
        seq = x[0]  # (seq, F)
        weights = np.linspace(0.5, 1.5, seq.shape[0])
        # axis=0 to weight timesteps
        weighted = np.average(seq, axis=0, weights=weights)
        weighted_mean = float(np.mean(weighted))
        sig = weighted_mean
    else:
        sig = float(np.mean(x))
    seed = _seed_from_array(x) ^ 0xA5A5A5A5
    rng = np.random.default_rng(seed)
    base = 1 / (1 + np.exp(- (sig * 2.8 - 0.6)))
    jitter = rng.uniform(-0.05, 0.05)
    return float(np.clip(base + jitter, 0.02, 0.98))


def demo_transformer(x: np.ndarray) -> float:
    if x.ndim == 3:
        seq = x[0]
        # attention-like: emphasize max deviation
        max_dev = float(np.max(np.abs(seq - np.mean(seq))))
        sig = float(np.mean(seq)) + max_dev * 0.3
    else:
        sig = float(np.mean(x))
    seed = _seed_from_array(x) ^ 0x5F5F5F5F
    rng = np.random.default_rng(seed)
    base = 1 / (1 + np.exp(- (sig * 3.0 - 0.7)))
    jitter = rng.uniform(-0.04, 0.04)
    return float(np.clip(base + jitter, 0.02, 0.98))


def demo_isolation_forest(x: np.ndarray) -> float:
    """Anomaly score in [0,1], higher = more anomalous."""
    # Use std + max as anomaly signal
    sig = float(np.std(x) * 1.5 + np.max(np.abs(x)) * 0.1)
    seed = _seed_from_array(x) ^ 0xC0FFEE
    rng = np.random.default_rng(seed)
    base = 1 / (1 + np.exp(- (sig * 2.0 - 1.0)))
    jitter = rng.uniform(-0.08, 0.08)
    return float(np.clip(base + jitter, 0.01, 0.95))


# Explanations generator for demo
def demo_explanations(features: dict, prob: float) -> list[str]:
    exps: list[str] = []
    syn = features.get("SYN Flag Cnt", features.get("syn_flag_cnt", 0))
    flow_pkts = features.get("Flow Pkts/s", features.get("flow_pkts_s", 0))
    byts = features.get("Flow Byts/s", features.get("flow_byts_s", 0))
    dur = features.get("Flow Duration", features.get("flow_duration", 0))

    if syn and float(syn) > 10:
        exps.append("↑ Abnormal SYN activity")
    if flow_pkts and float(flow_pkts) > 50:
        exps.append("↑ Increased connection rate")
    if byts and float(byts) > 20000:
        exps.append("↑ Unusual byte rate")
    if dur and float(dur) > 1000000:
        exps.append("↑ Prolonged flow duration")
    if not exps:
        if prob > 0.7:
            exps.append("↑ Destination distribution shift")
        elif prob > 0.4:
            exps.append("→ Mild traffic irregularity")
        else:
            exps.append("✓ Traffic within normal bounds")
    # Keep 3-4 items
    extra = []
    if prob > 0.8:
        extra.append("↑ Multiple temporal anomalies")
    if prob > 0.5:
        extra.append("→ Packet length variance elevated")
    exps.extend(extra)
    return exps[:4]
