from datetime import datetime, timezone

from src.application.services.repo_curve_service import RepoCurveService
from src.application.services.tick_state_store import _FutureState, _BondState
from src.core.models.calculations.gross_basis_calculations import GrossBasisCalcInput
from src.core.models.calculations.carry_calculations import CarryCalcInput


def gross_basis_calc_input_factory(future_state: _FutureState, bond_state: _BondState) -> GrossBasisCalcInput:
    return GrossBasisCalcInput(
        future_id=future_state.future.ContractSymbol,
        bond_id=bond_state.bond.ISIN,
        input_timestamp=datetime.now(timezone.utc),
        bond_bid=bond_state.bid,
        bond_ask=bond_state.ask,
        bond_bid_timestamp=bond_state.bid_timestamp,
        bond_ask_timestamp=bond_state.ask_timestamp,
        futures_bid=future_state.bid,
        futures_ask=future_state.ask,
        futures_bid_timestamp=future_state.bid_timestamp,
        futures_ask_timestamp=future_state.ask_timestamp,
        conversion_factor=bond_state.bond.get_conversion_factor(future_state.future.ContractSymbol),
    )

def carry_calc_input_factory(bond_state: _BondState, future_state: _FutureState, repo_curve_service: RepoCurveService) -> CarryCalcInput:
    return CarryCalcInput(
        clean_price = (bond_state.bid + bond_state.ask) / 2,
        coupon_rate = bond_state.bond.coupon_rate,
        delivery_date = bond_state.bond.next_delivery_date,
        repo_rate = repo_curve_service.get_rate(future_state.delivery_date),
        next_coupon_date = bond_state.bond.next_coupon_date,
        last_coupon_date = bond_state.bond.last_coupon_date,
        coupon_income_day_convention = "ACT/ACT",
        financing_day_convention = "ACT/365"
    )
