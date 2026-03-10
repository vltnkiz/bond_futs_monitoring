"""
carry_monitor_all_bonds.py  —  DRAFT

Carry monitor for all bonds in bond_definition.json.

Carry needs only: bond clean price + repo rate + bond static data (coupon,
coupon dates).  Future *prices* are not required — each future's delivery
date is used solely as a static horizon for the repo rate lookup.

Architecture
============

    ┌─────────────────────────────────────────────────────────────────┐
    │  LSEG feed (dedicated thread inside LSEGMarketDataFeed)         │
    │    bonds (all ISINs) + repo RICs  — no future price streams     │
    └───────────────────────────────┬─────────────────────────────────┘
                                    │ on_tick  →  tick_queue (Queue)
                                    ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │  Consumer thread                                                 │
    │                                                                  │
    │   repo tick  ──►  RepoCurveService.on_tick()                    │
    │                       (updates InterpolatedCurve in-place)      │
    │                       └─► _recalc_all_bonds()                   │
    │                                                                  │
    │   bond tick  ──►  _bond_states[isin].update(tick)               │
    │                       └─► _recalc_bond(isin)                    │
    └───────────────────────────────┬─────────────────────────────────┘
                                    │ CarryCalcInput
                                    ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │  CarryCalculationEngine  (one shared instance)                   │
    │    →  on_result callback  (print / downstream handler)           │
    └──────────────────────────────────────────────────────────────────┘

Notes / TODOs
=============
- Repo RICs below are approximate — replace with verified LSEG tickers.
- Tenor dates in REPO_CURVE_RICS are static approximations; production code
  should compute them dynamically from today + standard money-market offsets.
- Each bond is computed against all delivery dates of contracts it is
  deliverable into (one carry result per (bond, contract) horizon pair).
- CarryCalcInput inherits future_id/bond_id/input_timestamp from CalcInput;
  we use the contract symbol as future_id even though no future price is used.
"""

import json
import queue
import threading
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Optional

from src.adapters.driven.lseg_market_data_feed import LSEGMarketDataFeed
from src.application.services.repo_curve_service import RepoCurveService
from src.core.calculation_engines.carry_calculation_engine import CarryCalculationEngine
from src.core.models.bond import Bond
from src.core.models.calculations.carry_calculations import CarryCalcInput
from src.core.models.tick import Tick


# ---------------------------------------------------------------------------
# Approximate EUR repo / OIS curve tickers  (LSEG RICs — update with real ones)
# Tenor dates are rolling from today (2026-03-10); recompute dynamically in prod.
# ---------------------------------------------------------------------------
REPO_CURVE_RICS: dict[str, date] = {
    "EUROND=TTKL": date(2026, 3, 11),   # overnight  (~ESTR)
    "EUR1WDP=CALP":   date(2026, 3, 17),   # 1 week
    "EUR3MIRS":   date(2026, 4, 14),   # 3 month
}

FIELDS = ["CF_BID", "CF_ASK"]


# ---------------------------------------------------------------------------
# Lightweight bond price state (no future price needed)
# ---------------------------------------------------------------------------

@dataclass
class _BondPriceState:
    bond: Bond
    bid: Optional[float] = None
    ask: Optional[float] = None

    def update(self, tick: Tick) -> None:
        if tick.bid is not None:
            self.bid = tick.bid
        if tick.ask is not None:
            self.ask = tick.ask

    @property
    def is_ready(self) -> bool:
        return self.bid is not None and self.ask is not None

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2


# ---------------------------------------------------------------------------
# Static data loaders
# ---------------------------------------------------------------------------

def _load_bonds() -> list[Bond]:
    with open("data/portfolios/bond_definition.json", "r") as f:
        bond_def: dict = json.load(f)
    return [
        Bond(
            ISIN=d["ISIN"],
            CouponRate=d["CouponRate"],
            MaturityDate=d["MaturityDate"],
            DayCountConv=d["DayCountConv"],
            CF=d.get("CF", {}),
            NextCouponDate=d.get("NextCouponDate"),
            LastCouponDate=d.get("LastCouponDate"),
        )
        for d in bond_def.values()
    ]


def _load_delivery_dates() -> dict[str, date]:
    """Returns {contract_symbol: delivery_date} from future_definition.json."""
    with open("data/portfolios/future_definition.json", "r") as f:
        future_def: dict = json.load(f)
    return {
        sym: date.fromisoformat(fd["DeliveryDate"])
        for sym, fd in future_def.items()
    }


def _isin_to_ric(isin: str) -> str:
    """DE0001135481  →  DE013548="""
    return f"{isin[0:2]}{isin[5:11]}="


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # ------------------------------------------------------------------
    # 1. Load static data
    # ------------------------------------------------------------------
    all_bonds = _load_bonds()
    delivery_dates = _load_delivery_dates()   # {contract: date}
    print(f"Loaded {len(all_bonds)} bonds, {len(delivery_dates)} delivery horizons")

    # ------------------------------------------------------------------
    # 2. Build RIC ↔ ISIN mappings, subscribe only bonds + repo
    # ------------------------------------------------------------------
    bond_ric_to_isin: dict[str, str] = {_isin_to_ric(b.ISIN): b.ISIN for b in all_bonds}

    all_instruments = (
        sorted(bond_ric_to_isin.keys())
        + list(REPO_CURVE_RICS.keys())
    )
    print(f"Subscribing to {len(all_instruments)} instruments "
          f"({len(bond_ric_to_isin)} bonds, {len(REPO_CURVE_RICS)} repo tenors)")

    # ------------------------------------------------------------------
    # 3. State
    # ------------------------------------------------------------------
    repo_curve_service = RepoCurveService(ric_to_tenor=REPO_CURVE_RICS)
    bond_states: dict[str, _BondPriceState] = {
        b.ISIN: _BondPriceState(bond=b) for b in all_bonds
    }
    engine = CarryCalculationEngine()
    engine.subscribe(lambda r: print(f"[CARRY] {r.future_id} | {r.bond_id}: {r.carry:.4f}"))

    # ------------------------------------------------------------------
    # 4. Helpers to build CarryCalcInput and fire the engine
    # ------------------------------------------------------------------
    def _make_carry_inputs(state: _BondPriceState) -> list[CarryCalcInput]:
        """
        One input per futures contract the bond is deliverable into,
        using that contract's delivery date as the repo / carry horizon.
        """
        bond = state.bond
        inputs = []
        for contract_symbol, delivery_date in delivery_dates.items():
            if contract_symbol not in bond.CF:
                continue  # bond is not deliverable into this contract
            try:
                repo_rate = repo_curve_service.get_rate(delivery_date)
            except ValueError:
                continue  # curve not yet populated enough to interpolate
            inputs.append(CarryCalcInput(
                future_id=contract_symbol,
                bond_id=bond.ISIN,
                input_timestamp=datetime.now(timezone.utc),
                clean_price=state.mid,
                coupon_rate=bond.CouponRate,
                delivery_date=delivery_date,
                repo_rate=repo_rate,
                next_coupon_date=datetime.fromisoformat(bond.NextCouponDate),
                last_coupon_date=datetime.fromisoformat(bond.LastCouponDate),
            ))
        return inputs

    def _recalc_bond(isin: str) -> None:
        state = bond_states[isin]
        if not state.is_ready:
            return
        for calc_input in _make_carry_inputs(state):
            engine.on_calc_input(calc_input)

    def _recalc_all_bonds() -> None:
        for isin in bond_states:
            _recalc_bond(isin)

    # ------------------------------------------------------------------
    # 5. tick_queue separates LSEG feed thread from recalc processing
    # ------------------------------------------------------------------
    tick_queue: queue.Queue = queue.Queue()

    # ------------------------------------------------------------------
    # 6. LSEG streaming feed
    # ------------------------------------------------------------------
    feed = LSEGMarketDataFeed()
    feed.subscribe(instruments=all_instruments, fields=FIELDS)
    feed.start(on_tick=lambda tick: tick_queue.put(tick))

    # ------------------------------------------------------------------
    # 7. Consumer thread — routes ticks, no future price handling needed
    # ------------------------------------------------------------------
    def _consume() -> None:
        while True:
            tick = tick_queue.get()

            if tick.ric in REPO_CURVE_RICS:
                repo_curve_service.on_tick(tick)
                _recalc_all_bonds()

            elif tick.ric in bond_ric_to_isin:
                isin = bond_ric_to_isin[tick.ric]
                tick.ric = isin
                bond_states[isin].update(tick)
                _recalc_bond(isin)

    consumer = threading.Thread(target=_consume, daemon=True, name="carry-consumer")
    consumer.start()

    print("Carry monitor running. Press Ctrl+C to stop.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        feed.stop()
        print("Stopped.")
