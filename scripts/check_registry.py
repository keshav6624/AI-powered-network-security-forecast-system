"""Print predictor availability using the application model registry."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.model_loader import get_registry  # noqa: E402


def main() -> int:
    registry = get_registry()
    statuses = registry.status_list()
    for model in statuses:
        print(
            f"{model['display_name']}: {model['status']} "
            f"(available={model['available']}, demo={model['demo']})"
        )
    return 0 if any(model["available"] for model in statuses) else 1


if __name__ == "__main__":
    raise SystemExit(main())
