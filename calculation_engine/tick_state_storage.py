from datetime import datetime
from typing import Callable
    
from calculation_engine.gross_basis_calculation_engine import GrossBasisResult
from calculation_engine.models import BasisCalcInput, BondState, DeliverableBasket, FuturesContract, FuturesState

class TickStateStore:
    def __init__(self, basket: DeliverableBasket, futures: FuturesContract):
        self._bonds: dict[str, BondState] = {
            isin: BondState(isin=isin, conversion_factor=entry.conversion_factor)
            for isin, entry in basket.entries.items()
        }
        self._futures = FuturesState(ric=futures.ric)
        self._callbacks: list[Callable[[BasisCalcInput], None]] = []
        self._gross_basis: float = 0.0

    def subscribe(self, cb: Callable[[BasisCalcInput], None]) -> None:
        self._callbacks.append(cb)

    def update_bond(self, isin: str, bid: float | None, ask: float | None, ts: datetime) -> None:
        bond = self._bonds.get(isin)
        if bond is None:
            return
        if bid is not None:
            bond.bid = bid
        if ask is not None:
            bond.ask = ask
        bond.last_updated = ts
        self._notify(bond)

    def update_futures(self, bid: float | None, ask: float | None, ts: datetime) -> None:
        if bid is not None:
            self._futures.bid = bid
        if ask is not None:
            self._futures.ask = ask
        self._futures.last_updated = ts
        for bond in self._bonds.values():
            self._notify(bond)
    
    def update_gross_basis(self, gross_basis_result: GrossBasisResult) -> None:
        print(f"Updated gross basis: {gross_basis_result.gross_basis:.4f}")
        self._gross_basis = gross_basis_result.gross_basis

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