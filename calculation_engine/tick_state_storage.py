from dataclasses import dataclass
from datetime import datetime
from typing import Callable

@dataclass
class BasketEntry:
    isin: str
    conversion_factor: float

@dataclass
class DeliverableBasket:
    entries: dict[str, BasketEntry]

@dataclass
class FuturesContract:
    ric: str

@dataclass
class BondState:
    isin: str
    conversion_factor: float
    bid: float | None = None
    ask: float | None = None
    last_updated: datetime | None = None

@dataclass
class FuturesState:
    ric: str
    bid: float | None = None
    ask: float | None = None
    last_updated: datetime | None = None

@dataclass(frozen=True)
class BasisCalcInput:
    isin: str
    bond_bid: float
    bond_ask: float
    conversion_factor: float
    futures_bid: float
    futures_ask: float
    bond_tick_ts: datetime
    futures_tick_ts: datetime

class TickStateStore:
    def __init__(self, basket: DeliverableBasket, futures: FuturesContract):
        self._bonds: dict[str, BondState] = {
            isin: BondState(isin=isin, conversion_factor=entry.conversion_factor)
            for isin, entry in basket.entries.items()
        }
        self._futures = FuturesState(ric=futures.ric)
        self._callbacks: list[Callable[[BasisCalcInput], None]] = []

    def subscribe(self, cb: Callable[[BasisCalcInput], None]) -> None:
        self._callbacks.append(cb)

    def update_bond(self, isin: str, bid: float, ask: float, ts: datetime) -> None:
        bond = self._bonds.get(isin)
        if bond is None:
            return
        bond.bid = bid
        bond.ask = ask
        bond.last_updated = ts
        self._notify(bond)

    def update_futures(self, bid: float, ask: float, ts: datetime) -> None:
        self._futures.bid = bid
        self._futures.ask = ask
        self._futures.last_updated = ts
        for bond in self._bonds.values():
            self._notify(bond)

    def _notify(self, bond: BondState) -> None:
        f = self._futures
        if any(v is None for v in [bond.bid, bond.ask, f.bid, f.ask]):
            return
        snapshot = BasisCalcInput(
            isin=bond.isin,
            bond_bid=bond.bid,
            bond_ask=bond.ask,
            conversion_factor=bond.conversion_factor,
            futures_bid=f.bid,
            futures_ask=f.ask,
            bond_tick_ts=bond.last_updated,
            futures_tick_ts=f.last_updated,
        )
        for cb in self._callbacks:
            cb(snapshot)