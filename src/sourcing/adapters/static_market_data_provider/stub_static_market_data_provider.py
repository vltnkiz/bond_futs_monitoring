from typing import Dict, Optional, Tuple

from src.sourcing.core.ports import MarketDataProvider


class StubStaticMarketDataProvider(MarketDataProvider):
    def __init__(self, data: Dict[Tuple[str, str], str]):
        self._data = data

    def get(self, ric: str, field: str) -> Optional[str]:
        return self._data.get((ric, field))
