from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Generic, TypeVar

from src.core.models.bond import Bond
from src.core.models.future import Future
from src.core.models.calculations import CalcInput

TCalcInput = TypeVar("TCalcInput", bound=CalcInput)

@dataclass
class StalenessConfig:
    max_bond_quote_age: timedelta        # max age of bond bid or ask individually
    max_futures_quote_age: timedelta     # max age of futures bid or ask individually
    max_cross_instrument_age: timedelta  # max age difference between bond and futures snapshots

@dataclass
class _FutureState():
    future: Future
    bid: float | None = None
    ask: float | None = None
    bid_timestamp: datetime | None = None
    ask_timestamp: datetime | None = None

@dataclass
class _BondState():
    bond: Bond
    bid: float | None = None
    ask: float | None = None
    bid_timestamp: datetime | None = None
    ask_timestamp: datetime | None = None

class TickStateStore:

    def __init__(
        self,
        future: Future,
        bonds: list[Bond],
        calc_input_factory: Callable[[_FutureState, _BondState], TCalcInput],
        staleness_config: StalenessConfig,
    ) -> None: 
        self._future: _FutureState = _FutureState(future=future)      
        self._bonds: dict[str, _BondState] = {bond.ISIN: _BondState(bond=bond) for bond in bonds}
        self._calc_input_factory = calc_input_factory
        self._callbacks: list[Callable[[TCalcInput], None]] = []
        self._staleness_config = staleness_config
        

    def update_bond(
        self,
        isin: str,
        bid: float | None,
        ask: float | None,
        bid_ts: datetime | None,
        ask_ts: datetime | None,
    ) -> None: 
        if isin not in self._bonds:
            return
        
        bond_state = self._bonds[isin]
        bond_state.bid = bid
        bond_state.ask = ask
        bond_state.bid_timestamp = bid_ts
        bond_state.ask_timestamp = ask_ts

        self._notify(bond=bond_state)

    def update_future(
        self,
        bid: float | None,
        ask: float | None,
        bid_ts: datetime | None,
        ask_ts: datetime | None,
    ) -> None:
        self._future.bid = bid
        self._future.ask = ask
        self._future.bid_timestamp = bid_ts
        self._future.ask_timestamp = ask_ts

        self._notify(future=self._future)

    def subscribe(self, cb: Callable[[TCalcInput], None]) -> None:
        self._callbacks.append(cb)

    def _is_valid_snapshot(self, bond: _BondState) -> bool:
        if self._future.bid is None or self._future.ask is None:
            return False
        if bond.bid is None or bond.ask is None:
            return False
            
        now = datetime.now()
        # Check individual staleness
        if self._future.bid_timestamp is None or self._future.ask_timestamp is None:
            return False
        if now - self._future.bid_timestamp > self._staleness_config.max_futures_quote_age:
            return False
        if now - self._future.ask_timestamp > self._staleness_config.max_futures_quote_age:
            return False
        if bond.bid_timestamp is None or bond.ask_timestamp is None:
            return False
        if now - bond.bid_timestamp > self._staleness_config.max_bond_quote_age:
            return False
        if now - bond.ask_timestamp > self._staleness_config.max_bond_quote_age:
            return False
            
        # Check cross-instrument staleness
        if abs((self._future.bid_timestamp - bond.bid_timestamp).total_seconds()) > self._staleness_config.max_cross_instrument_age.total_seconds():
            return False
        if abs((self._future.ask_timestamp - bond.ask_timestamp).total_seconds()) > self._staleness_config.max_cross_instrument_age.total_seconds():
            return False
        
        return True

    def _notify(self, future: _FutureState = None, bond: _BondState = None) -> None:
        if future is not None:
            for bond_state in self._bonds.values():
                if self._is_valid_snapshot(bond_state):
                    calc_input = self._calc_input_factory(future, bond_state)
                    for cb in self._callbacks:
                        cb(calc_input)
        elif bond is not None:
            if self._is_valid_snapshot(bond):
                calc_input = self._calc_input_factory(self._future, bond)
                for cb in self._callbacks:
                    cb(calc_input)