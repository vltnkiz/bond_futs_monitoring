from abc import ABC, abstractmethod
from datetime import date

class RateCurve(ABC):
    @abstractmethod
    def get_rate(self, settlement_date: date) -> float:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Curve identifier for logging/output."""
        raise NotImplementedError