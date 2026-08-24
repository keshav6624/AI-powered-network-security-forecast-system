"""Verify all trained artifacts load successfully — no predictions yet."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

mp = ROOT / "models"

results = []

def report(name: str, ok: bool, msg: str = ""):
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if msg:
        line += f" — {msg}"
    print(line)
    results.append((name, ok, msg))


print("=" * 60)
print("MODEL VERIFICATION")
print("=" * 60)

# 1) JSON files
try:
    feature_cols = json.loads((mp / "preprocessing" / "feature_columns.json").read_text())
    report("Feature Columns", isinstance(feature_cols, list) and len(feature_cols) > 0, f"{len(feature_cols)} columns")
except Exception as e:
    report("Feature Columns", False, str(e))
    feature_cols = []

try:
    metadata = json.loads((mp / "metadata" / "model_metadata.json").read_text())
    seq_len = int(metadata.get("sequence_length", 0))
    report("Metadata", seq_len > 0, f"sequence_length={seq_len}, features_in_meta={len(metadata.get('features', []))}")
except Exception as e:
    report("Metadata", False, str(e))
    seq_len = 0

try:
    csv_text = (mp / "metadata" / "model_comparison.csv").read_text()
    report("Model Comparison", "Model," in csv_text, "CSV readable")
except Exception as e:
    report("Model Comparison", False, str(e))

# 2) Scaler
try:
    import joblib
    scaler = joblib.load(mp / "preprocessing" / "network_state_scaler.joblib")
    report("Network Scaler", scaler.n_features_in_ == 28, f"type={type(scaler).__name__}, n_features={scaler.n_features_in_}")
except Exception as e:
    report("Network Scaler", False, str(e))

# 3) Logistic Regression
try:
    import joblib
    log = joblib.load(mp / "baseline" / "logistic_baseline.joblib")
    n_feats = getattr(log, "n_features_in_", 0)
    report("Logistic Regression", n_feats == 28, f"type={type(log).__name__}, n_features={n_feats}")
except Exception as e:
    report("Logistic Regression", False, str(e))

# 4) XGBoost
try:
    import xgboost as xgb
    b = xgb.Booster()
    b.load_model(str(mp / "xgboost" / "xgboost_model.json"))
    report("XGBoost", b.num_features() == 28, f"num_features={b.num_features()}, rounds={b.num_boosted_rounds()}")
except Exception as e:
    report("XGBoost", False, str(e))

# 5) LSTM
try:
    from tensorflow import keras
    lstm = keras.models.load_model(str(mp / "lstm" / "lstm_world_model.keras"))
    in_shape = lstm.input_shape
    out_shape = lstm.output_shape
    expected = (None, seq_len, 28)
    report("LSTM", in_shape == expected or (in_shape and in_shape[-2:] == (seq_len, 28)),
           f"input_shape={in_shape}, output_shape={out_shape}")
except Exception as e:
    report("LSTM", False, str(e)[:200])

# 6) Temporal Transformer
try:
    from tensorflow import keras
    tx = keras.models.load_model(str(mp / "transformer" / "temporal_transformer.keras"))
    in_shape = tx.input_shape
    out_shape = tx.output_shape
    report("Temporal Transformer", in_shape and in_shape[-2:] == (seq_len, 28),
           f"input_shape={in_shape}, output_shape={out_shape}")
except Exception as e:
    report("Temporal Transformer", False, str(e)[:200])

# 7) Isolation Forest
try:
    import joblib
    iso = joblib.load(mp / "isolation_forest" / "isolation_forest.joblib")
    report("Isolation Forest", hasattr(iso, "predict"), f"type={type(iso).__name__}")
except Exception as e:
    report("Isolation Forest", False, str(e))

# 8) network_states.csv
try:
    csv_text = (mp / "data" / "network_states.csv").read_text()
    lines = csv_text.count("\n")
    report("Network States CSV", lines > 100, f"{lines} lines")
except Exception as e:
    report("Network States CSV", False, str(e))

# 9) Registry
try:
    reg = json.loads((mp / "model_registry.json").read_text())
    report("Model Registry", "models" in reg, f"5 entries" if len(reg.get("models", {})) == 5 else f"{len(reg.get('models', {}))} entries")
except Exception as e:
    report("Model Registry", False, str(e))

print("=" * 60)
ok_count = sum(1 for _, o, _ in results if o)
total = len(results)
if ok_count == total:
    print("STATUS: ALL MODELS READY")
else:
    print(f"STATUS: {ok_count}/{total} models ready")
print("=" * 60)
sys.exit(0 if ok_count == total else 1)
