from datetime import datetime, timezone

from src.application.tick_state_store import _FutureState, _BondState
from src.core.models.calculations import GrossBasisCalcInput


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
