from datetime import date, datetime, timezone

from src.application.services.repo_curve_service import RepoCurveService
from src.application.services.tick_state_store import _FutureState, _BondState
from src.core.models.bond import Bond
from src.core.models.future import Future
from src.core.models.tick import Tick
from src.core.models.calculations.gross_basis_calculations import GrossBasisCalcInput
from src.core.models.calculations.carry_calculations import CarryCalcInput


def gross_basis_calc_input_factory(future_state: _FutureState, bond_state: _BondState) -> GrossBasisCalcInput:
    return GrossBasisCalcInput(
        future_id=future_state.future.ContractSymbol,
        bond_id=bond_state.bond.ISIN,
        input_timestamp=datetime.now(timezone.utc),
        bond_bid=bond_state.tick.bid,
        bond_ask=bond_state.tick.ask,
        bond_bid_timestamp=bond_state.tick.bid_timestamp,
        bond_ask_timestamp=bond_state.tick.ask_timestamp,
        futures_bid=future_state.tick.bid,
        futures_ask=future_state.tick.ask,
        futures_bid_timestamp=future_state.tick.bid_timestamp,
        futures_ask_timestamp=future_state.tick.ask_timestamp,
        conversion_factor=bond_state.bond.get_conversion_factor(future_state.future.ContractSymbol),
    )


def carry_calc_input_factory(bond: Bond, tick: Tick, future: Future, repo_service: RepoCurveService) -> CarryCalcInput:
    delivery_date = date.fromisoformat(future.DeliveryDate)
    return CarryCalcInput(
        future_id=future.ContractSymbol,
        bond_id=bond.ISIN,
        input_timestamp=datetime.now(timezone.utc),
        clean_price=(tick.bid + tick.ask) / 2,
        coupon_rate=bond.CouponRate,
        delivery_date=delivery_date,
        repo_rate=repo_service.get_rate(delivery_date),
        next_coupon_date=datetime.fromisoformat(bond.NextCouponDate),
        last_coupon_date=datetime.fromisoformat(bond.LastCouponDate),
    )
