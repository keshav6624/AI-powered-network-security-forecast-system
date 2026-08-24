"""
BasePredictor — common interface for all 5 models
"""
from abc import ABC, abstractmethod
from typing import Optional
import time
import numpy as np


class BasePredictor(ABC):
    name: str = "base"
    display_name: str = "Base"

    def __init__(self):
        self._available: bool = False
        self._demo: bool = False
        self._load_error: Optional[str] = None

    @abstractmethod
    def load(self) -> bool:
        """Try to load artifact. Return True if available. Must not raise."""

    def is_available(self) -> bool:
        return self._available

    def is_demo(self) -> bool:
        return self._demo

    def load_error(self) -> Optional[str]:
        return self._load_error

    @abstractmethod
    def predict_proba(self, x: np.ndarray) -> float:
        """Return attack probability in [0,1] for single window or sequence."""

    def predict(self, x: np.ndarray, threshold: float = 0.5) -> int:
        return int(self.predict_proba(x) >= threshold)

    def timed_proba(self, x: np.ndarray) -> tuple[float, float]:
        t0 = time.perf_counter()
        p = self.predict_proba(x)
        dt = (time.perf_counter() - t0) * 1000.0
        return p, dt
