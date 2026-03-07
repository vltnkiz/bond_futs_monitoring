from abc import ABC, abstractmethod

from src.core.models.tick_handler import TickHandler

class MarketDataFeed(ABC):
    @abstractmethod
    def subscribe(self, instruments: list[str], fields: list[str]) -> None:
        raise NotImplementedError()
    
    @abstractmethod
    def unsubscribe(self, instruments: list[str]) -> None:
        raise NotImplementedError()
    
    @abstractmethod
    def add_instruments(self, instruments: list[str]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def start(self, on_tick: TickHandler) -> None:
        raise NotImplementedError()

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError()

    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError()