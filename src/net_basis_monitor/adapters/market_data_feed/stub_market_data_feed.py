from typing import List, Optional, Set

from src.net_basis_monitor.core.models.value_objects.tick import Tick, TickHandler
from src.net_basis_monitor.core.ports.market_data_feed import MarketDataFeed


class StubMarketDataFeed(MarketDataFeed):
    def __init__(self):
        self._subscribed_instruments: Set[str] = set()
        self._subscribed_fields: Set[str] = set()
        self._callback: Optional[TickHandler] = None
        self._connected: bool = False
    
    def subscribe(self, instruments: List[str], fields: List[str]) -> None:
        self._subscribed_instruments.update(instruments)
        self._subscribed_fields.update(fields)
        self._connected = True

    def unsubscribe(self, instruments: List[str]) -> None:
        self._subscribed_instruments.difference_update(instruments)

    def add_instruments(self, instruments: List[str]) -> None:
        self._subscribed_instruments.update(instruments)

    def start(self, on_tick: TickHandler) -> None:
        self._callback = on_tick
        self._connected = True

    def stop(self) -> None:
        self._callback = None
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    @property
    def provider_name(self) -> str:
        return "Stub"

    def push_update(self, tick: Tick) -> None:
        if self._callback:
            self._callback(tick)
    
    def get_subscribed_instruments(self) -> Set[str]:
        return self._subscribed_instruments
