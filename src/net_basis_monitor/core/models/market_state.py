import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from src.net_basis_monitor.core.models.value_objects.bond import Bond
from src.net_basis_monitor.core.models.value_objects.future import Future
from src.net_basis_monitor.core.models.value_objects.tick import Tick

logger = logging.getLogger(__name__)

InstrumentT = TypeVar("InstrumentT")


@dataclass
class MarketState(ABC, Generic[InstrumentT]):
    instrument: InstrumentT
    _last_tick: Optional[Tick] = field(default=None, init=False)

    def on_tick(self, tick: Tick) -> None:
        logger.debug("Received tick for %s: %s", self.instrument_id, tick)
        if tick.bid is not None and tick.ask is not None:
            tick.mid = (tick.bid + tick.ask) / 2.0
        self._last_tick = tick

    @property
    def last_tick(self) -> Optional[Tick]:
        return self._last_tick

    @property
    def mid_price(self) -> Optional[float]:
        if not self._last_tick:
            return None
        
        if self._last_tick.mid is not None:
            return self._last_tick.mid
        
        if self._last_tick.bid is not None and self._last_tick.ask is not None:
            return (self._last_tick.bid + self._last_tick.ask) / 2.0
            
        return None

    def is_stale(self, max_age_seconds: int = 60) -> bool:
        if not self._last_tick or not self._last_tick.timestamp:
            return True
        # Assuming tick timestamp is timezone aware (UTC)
        age = datetime.now(timezone.utc) - self._last_tick.timestamp
        return age.total_seconds() > max_age_seconds

    @property
    @abstractmethod
    def instrument_id(self) -> str:
        pass


@dataclass
class BondMarketState(MarketState[Bond]):
    @property
    def instrument_id(self) -> str:
        return self.instrument.lseg_ric


@dataclass
class FutureMarketState(MarketState[Future]):
    @property
    def instrument_id(self) -> str:
        return self.instrument.contract_symbol