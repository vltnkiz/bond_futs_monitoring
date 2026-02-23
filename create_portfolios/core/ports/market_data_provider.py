from abc import ABC, abstractmethod
from typing import Optional


class MarketDataProvider(ABC):
    @abstractmethod
    def get(self, ric: str, field: str) -> Optional[str]:
        pass
