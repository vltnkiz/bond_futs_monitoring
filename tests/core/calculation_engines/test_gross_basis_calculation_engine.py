from datetime import datetime, timezone

import pytest

from src.core.calculation_engines.gross_basis_calculation_engine import GrossBasisCalculationEngine
from src.core.models.calculations import GrossBasisCalcInput


_NOW = datetime(2026, 3, 7, 12, 0, 0, tzinfo=timezone.utc)


def make_input(
    bond_bid: float = 99.0,
    bond_ask: float = 99.5,
    futures_bid: float = 100.0,
    futures_ask: float = 100.5,
    conversion_factor: float = 1.0,
    future_id: str = "FGBL Jun26",
    bond_id: str = "DE0001102614",
) -> GrossBasisCalcInput:
    return GrossBasisCalcInput(
        future_id=future_id,
        bond_id=bond_id,
        input_timestamp=_NOW,
        bond_bid=bond_bid,
        bond_ask=bond_ask,
        futures_bid=futures_bid,
        futures_ask=futures_ask,
        bond_bid_timestamp=_NOW,
        bond_ask_timestamp=_NOW,
        futures_bid_timestamp=_NOW,
        futures_ask_timestamp=_NOW,
        conversion_factor=conversion_factor,
    )

@pytest.mark.parametrize("bond_bid,bond_ask,futures_bid,futures_ask,cf,expected", [
    # bond_mid=100, futures_mid=100, CF=1  →  0
    (100.0, 100.0, 100.0, 100.0, 1.0,  0.0),
    # bond_mid=99.5, futures_mid=100.25, CF=0.95  →  99.5 - 100.25*0.95 = 4.2625
    (99.0,  100.0,  99.5, 101.0, 0.95, 4.2625),
    # negative gross basis: bond_mid=98, futures_mid=100, CF=1  →  -2
    (98.0,  98.0,  100.0, 100.0, 1.0, -2.0),
])
def test_gross_basis_formula(bond_bid, bond_ask, futures_bid, futures_ask, cf, expected):
    """gross_basis = (bond_bid+bond_ask)/2 - (futures_bid+futures_ask)/2 * CF."""
    engine = GrossBasisCalculationEngine()
    result = engine._compute(make_input(
        bond_bid=bond_bid, bond_ask=bond_ask,
        futures_bid=futures_bid, futures_ask=futures_ask,
        conversion_factor=cf,
    ))
    assert result is not None
    assert result.gross_basis == pytest.approx(expected)