"""
Replay Engine — simulates real-time traffic from processed CIC-IDS2018.

Reads sample/processed windows and steps through them, calling ForecastingService.

Speeds: 1x, 5x, 10x — controls delay between windows (used by frontend polling too).
State is in-memory (singleton); persists predictions/alerts to DB when stepping.
"""
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.forecasting import ForecastingService

logger = get_logger(__name__)

class ReplayEngine:
    def __init__(self):
        self.settings = get_settings()
        self.windows: List[dict] = []
        self.idx: int = 0
        self.running: bool = False
        self.speed: str = self.settings.replay_default_speed  # 1x | 5x | 10x
        self.history: List[dict] = []  # recent predictions
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._load_windows()

    def _load_windows(self) -> None:
        # Prefer data/sample/sample_windows.json, then data/processed/sample_windows.json, then synthetic
        candidates = [
            Path(self.settings.replay_sample_path) / "sample_windows.json",
            Path("./data/sample/sample_windows.json"),
            Path("./data/processed/sample_windows.json"),
            Path("data/sample/sample_windows.json"),
        ]
        for p in candidates:
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    if isinstance(data, list) and data:
                        self.windows = data
                        logger.info("replay_windows_loaded", path=str(p), count=len(data))
                        return
                except Exception as e:
                    logger.warning("replay_load_failed", path=str(p), error=str(e))
        # Fallback synthetic (ensures engine works without dataset)
        logger.warning("replay_using_synthetic")
        self.windows = self._synthetic_windows(200)

    def _synthetic_windows(self, n: int) -> List[dict]:
        import random, math
        windows = []
        base = datetime.now(timezone.utc)
        for i in range(n):
            # Create temporal drift: slowly increase suspiciousness then reset
            phase = (i % 50) / 50.0
            suspicious = 1 if phase > 0.6 else 0
            # sine wave for interesting replay
            wave = math.sin(i * 0.2) * 0.3 + 0.5
            syn = 5 + int(wave * 40) if suspicious else 2 + int(random.random() * 3)
            flow_pkts = 80 + int(wave * 60) if suspicious else 10 + int(random.random() * 10)
            ts = base.isoformat()
            windows.append({
                "window_id": f"syn-{i:04d}",
                "timestamp": ts,
                "features": {
                    "Flow Duration": 120 + i * 3 + syn * 10,
                    "Tot Fwd Pkts": 10 + syn,
                    "Tot Bwd Pkts": 8,
                    "Flow Byts/s": 5000 + syn * 1200,
                    "Flow Pkts/s": flow_pkts,
                    "Fwd Pkts/s": 6 + syn * 0.8,
                    "Bwd Pkts/s": 6,
                    "Pkt Len Mean": 200 - syn * 2,
                    "SYN Flag Cnt": syn,
                    "RST Flag Cnt": 1 if suspicious else 0,
                    "Active Mean": 0.5 + wave * 0.4,
                    "Idle Mean": 0.1,
                },
                "label": "Suspicious" if suspicious else "Benign",
            })
        return windows

    def reload(self) -> None:
        with self._lock:
            self._load_windows()
            self.idx = 0
            self.history.clear()

    def status(self) -> dict:
        with self._lock:
            cur = self.windows[self.idx] if self.windows and 0 <= self.idx < len(self.windows) else None
            last_pred = self.history[-1] if self.history else None
        return {
            "running": self.running,
            "speed": self.speed,
            "total_windows": len(self.windows),
            "current_index": self.idx,
            "current_window": cur,
            "last_prediction": last_pred,
            "progress": round(self.idx / max(len(self.windows), 1) * 100, 1),
            "demo_mode": self.settings.demo_mode,
        }

    def set_speed(self, speed: str) -> bool:
        if speed not in ("1x", "5x", "10x"):
            return False
        self.speed = speed
        logger.info("replay_speed_set", speed=speed)
        return True

    def step(self, db=None) -> Optional[dict]:
        """Single step: predict current window, advance idx."""
        with self._lock:
            if not self.windows:
                return None
            if self.idx >= len(self.windows):
                self.idx = 0  # loop
            win = self.windows[self.idx]
            self.idx += 1

        features = win.get("features", {})
        # Build sequence from recent history windows
        with self._lock:
            seq = [w.get("features", {}) for w in self.windows[max(0, self.idx - 11): self.idx - 1]]

        svc = ForecastingService()
        # db injected by caller when available
        result = svc.predict(features=features, sequence=seq, db=db)
        # annotate
        result["window_id"] = win.get("window_id")
        result["window_label"] = win.get("label")

        with self._lock:
            self.history.append(result)
            # keep last 200
            if len(self.history) > 200:
                self.history = self.history[-200:]
        logger.info("replay_step", idx=self.idx, prob=result["forecast"]["attack_probability"], risk=result["risk"]["level"])
        return result

    def start(self) -> bool:
        if self.running:
            return False
        self.running = True
        self._stop_event.clear()

        def loop():
            from app.database.database import SessionLocal
            while not self._stop_event.is_set():
                try:
                    db = SessionLocal()
                    try:
                        self.step(db=db)
                    finally:
                        db.close()
                except Exception as e:
                    logger.error("replay_loop_error", error=str(e))
                # delay based on speed
                delays = {"1x": 1.5, "5x": 0.4, "10x": 0.15}
                delay = delays.get(self.speed, 1.5)
                self._stop_event.wait(delay)
                # auto stop at end
                if self.idx >= len(self.windows):
                    logger.info("replay_completed_loop")
                    # loop anyway; or stop — we loop
            self.running = False

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
        logger.info("replay_started", speed=self.speed)
        return True

    def stop(self) -> bool:
        if not self.running:
            return False
        self._stop_event.set()
        self.running = False
        logger.info("replay_stopped")
        return True

    def reset(self) -> None:
        self.stop()
        with self._lock:
            self.idx = 0
            self.history.clear()


# Singleton
_replay: Optional[ReplayEngine] = None

def get_replay_engine() -> ReplayEngine:
    global _replay
    if _replay is None:
        _replay = ReplayEngine()
    return _replay
