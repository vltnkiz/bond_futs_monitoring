from abc import ABC, abstractmethod
from typing import Callable

from market_data_feed.core.models.tick import Tick

TickHandler = Callable[[Tick], None]

class MarketDataFeed(ABC):
    @abstractmethod
    def subscribe(self, instruments: list[str], fields: list[str]) -> None:
        return NotImplementedError
    
    @abstractmethod
    def unsubscribe(self, instruments: list[str]) -> None:
        return NotImplementedError
    
    @abstractmethod
    def add_instruments(self, instruments: list[str]) -> None:
        return NotImplementedError

    @abstractmethod
    def start(self, on_tick: TickHandler) -> None:
        return NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        return NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        return NotImplementedError

    @property
    @abstractmethod
    def provider_name(self) -> str:
        return NotImplementedError