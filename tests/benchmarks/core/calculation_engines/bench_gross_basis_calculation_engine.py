from datetime import datetime, timezone

import pytest

from src.core.calculation_engines.gross_basis_calculation_engine import GrossBasisCalculationEngine
from src.core.models.calculations import GrossBasisCalcInput

_NOW = datetime(2026, 3, 7, 12, 0, 0, tzinfo=timezone.utc)

_INPUT = GrossBasisCalcInput(
    future_id="FGBL Jun26",
    bond_id="DE0001102614",
    input_timestamp=_NOW,
    bond_bid=99.50,
    bond_ask=99.52,
    futures_bid=100.10,
    futures_ask=100.12,
    bond_bid_timestamp=_NOW,
    bond_ask_timestamp=_NOW,
    futures_bid_timestamp=_NOW,
    futures_ask_timestamp=_NOW,
    conversion_factor=0.968432,
)


@pytest.mark.benchmark
def bench_gross_basis_compute(benchmark):
    engine = GrossBasisCalculationEngine()
    benchmark(engine._compute, _INPUT)


@pytest.mark.benchmark
def bench_gross_basis_on_calc_input(benchmark):
    """Includes subscriber dispatch overhead on top of the raw compute."""
    engine = GrossBasisCalculationEngine()
    engine.subscribe(lambda _: None)
    benchmark(engine.on_calc_input, _INPUT)
