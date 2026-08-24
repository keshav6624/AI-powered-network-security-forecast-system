"""Run one end-to-end forecast against a stored network state."""
import csv
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.forecasting import ForecastingService  # noqa: E402


def load_sample() -> dict[str, float]:
    states_path = PROJECT_ROOT / "models" / "data" / "network_states.csv"
    with states_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        row = next(reader, None)
    if row is None:
        raise RuntimeError(f"No network states found in {states_path}")
    return {
        key: float(value)
        for key, value in row.items()
        if key not in {"time_window", "target"} and value not in {None, ""}
    }


def main() -> int:
    features = load_sample()
    result = ForecastingService().predict(features=features, persist=False)
    print(f"Attack probability: {result['forecast']['attack_probability']:.2%}")
    print(f"Risk: {result['risk']['score']}/100 ({result['risk']['level']})")
    print(f"Models used: {', '.join(result['models']) or 'none'}")
    return 0 if result["models"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
