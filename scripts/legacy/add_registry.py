"""Append ModelRegistry class to model_loader.py"""
import pathlib

p = pathlib.Path(r"C:\Users\kesha\Downloads\AI-Powered Network Attack Forecasting System\backend\app\ml\model_loader.py")
lines = p.read_text(encoding="utf-8-sig").split("\n")

# Find the module-level _registry line and insert ModelRegistry after it
# Line 132 (0-indexed 131) is "_registry: Optional[ModelRegistry] = None"
# We want to insert ModelRegistry class after that line

insert_after = None
for i, line in enumerate(lines):
    if line.strip() == "_registry: Optional[ModelRegistry] = None":
        insert_after = i
        break

if insert_after is not None:
    # Insert ModelRegistry class starting after line insert_after
    # (so it goes after the _registry line, at module level before any class)
    model_registry_code = [
        "",
        'class ModelRegistry:',
        '    """Registry of all model predictors loaded via ModelLoader."""',
        "    def __init__(self, loader: 'ModelLoader'):",
        "        self.loader = loader",
        "        self.predictors: Dict[str, BasePredictor] = {}",
        "        self._load()",
        "",
        "    def _load(self) -> None:",
        "        from app.ml.predictors.logistic import LogisticPredictor",
        "        from app.ml.predictors.xgboost import XGBoostPredictor",
        "        from app.ml.predictors.lstm import LSTMPredictor",
        "        from app.ml.predictors.transformer import TransformerPredictor",
        "        from app.ml.predictors.isolation_forest import IsolationForestPredictor",
        "        from app.core.logging import get_logger",
        "        from app.ml.predictors.base import BasePredictor",
        "        logger = get_logger(__name__)",
        "        names = self.loader.predict_status()",
        "        for key, info in names.items():",
        "            if not info['status'].startswith('Available'):",
        "                continue",
        "            try:",
        "                if key == 'logistic_regression':",
        "                    p = LogisticPredictor()",
        "                    p.load()",
        "                    self.predictors[key] = p",
        "                elif key == 'xgboost':",
        "                    p = XGBoostPredictor()",
        "                    p.load()",
        "                    self.predictors[key] = p",
        "                elif key == 'lstm':",
        "                    p = LSTMPredictor()",
        "                    p.load()",
        "                    self.predictors[key] = p",
        "                elif key == 'transformer':",
        "                    p = TransformerPredictor()",
        "                    p.load()",
        "                    self.predictors[key] = p",
        "                elif key == 'isolation_forest':",
        "                    p = IsolationForestPredictor()",
        "                    p.load()",
        "                    self.predictors[key] = p",
        "                else:",
        "                    import logging",
        "                    logging.getLogger(__name__).warning('predictor_unknown', key=key)",
        "            except Exception as e:",
        "                import logging",
        "                logging.getLogger(__name__).warning('predictor_load_failed', key=key, error=str(e))",
        "                pass",
        "",
        "    def load_all(self) -> Dict[str, dict]:",
        "        \"\"\"Load all available models and return status dict.\"\"\"",
        "        result = {}",
        "        for key, pred in self.predictors.items():",
        "            result[key] = {",
        "                'name': pred.name,",
        "                'available': pred.is_available(),",
        "                'demo': pred.is_demo(),",
        "            }",
        "        return result",
    ]
    new_lines = lines[: insert_after + 1] + model_registry_code + lines[insert_after + 1 :]
    p.write_text("\n".join(new_lines), encoding="utf-8-sig")
    print(f"Inserted ModelRegistry class after line {insert_after + 1}")
else:
    print("Could not find _registry line to insert after")