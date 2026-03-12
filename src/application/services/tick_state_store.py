from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, Optional, TypeVar

from src.core.models.bond import Bond
from src.core.models.future import Future
from src.core.models.calculations.calculations import CalcInput
from src.core.models.tick import Tick

TCalcInput = TypeVar("TCalcInput", bound=CalcInput)

@dataclass
class StalenessConfig:
    max_bond_quote_age: timedelta = timedelta(seconds=30)
    max_futures_quote_age: timedelta = timedelta(seconds=30)
    max_cross_instrument_age: timedelta = timedelta(seconds=60)

@dataclass
class _FutureState:
    future: Future
    tick: Tick | None = None

@dataclass
class _BondState:
    bond: Bond
    tick: Tick | None = None

class TickStateStore:

    def __init__(
        self,
        future: Future,
        bonds: list[Bond],
        calc_input_factory: Callable[[_FutureState, _BondState], TCalcInput],
        staleness_config: Optional[StalenessConfig] = None,
    ) -> None:
        self._future: _FutureState = _FutureState(future=future)
        self._bonds: dict[str, _BondState] = {bond.ISIN: _BondState(bond=bond) for bond in bonds}
        self._calc_input_factory = calc_input_factory
        self._callbacks: list[Callable[[TCalcInput], None]] = []
        self._staleness_config = staleness_config or StalenessConfig()

    def update_bond(self, isin: str, tick: Tick) -> None:
        if isin not in self._bonds:
            return
        bond_state = self._bonds[isin]
        bond_state.tick = tick
        self._notify(bond=bond_state)

    def update_future(self, contract_symbol: str, tick: Tick) -> None:
        self._future.tick = tick
        self._notify(future=self._future)

    def subscribe(self, cb: Callable[[TCalcInput], None]) -> None:
        self._callbacks.append(cb)

    def _is_valid_snapshot(self, bond: _BondState) -> bool:
        if self._future.tick is None or bond.tick is None:
            return False
        if self._future.tick.bid is None or self._future.tick.ask is None:
            return False
        if bond.tick.bid is None or bond.tick.ask is None:
            return False
        if self._future.tick.is_stale(self._staleness_config.max_futures_quote_age):
            return False
        if bond.tick.is_stale(self._staleness_config.max_bond_quote_age):
            return False
        if self._future.tick.is_stale_relative_to(bond.tick, self._staleness_config.max_cross_instrument_age):
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