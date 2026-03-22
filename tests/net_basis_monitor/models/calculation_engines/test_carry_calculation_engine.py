from datetime import date, datetime, timezone

import pytest

from src.net_basis_monitor.core.models.calculation_engines.carry_calculation_engine import CarryCalculationEngine
from src.net_basis_monitor.core.models.calculation_params.carry_calculations import CarryCalcInput


def test_carry_de000bu2z049_fgblm26():
    fixture = Fixture(
        calc_input=CarryCalcInput(
            future_id="FGBLM26",
            bond_id="DE000BU2Z049",
            input_timestamp=datetime(2026, 3, 22, 12, 0, 0, tzinfo=timezone.utc),
            clean_price=96.172,
            coupon_rate=2.5,
            delivery_date=date(2026, 6, 10),
            settlement_date=date(2026, 3, 25),
            repo_rate=2.159,
            next_coupon_date=datetime(2027, 2, 15, tzinfo=timezone.utc),
            last_coupon_date=datetime(2026, 2, 16, tzinfo=timezone.utc),
        )
    )
    fixture.verify_carry_is_computed()
    fixture.verify_carry_value()


class Fixture:
    def __init__(self, calc_input: CarryCalcInput):
        self._engine = CarryCalculationEngine()
        self._result = self._engine.compute(calc_input)

    def verify_carry_is_computed(self):
        assert self._result is not None
        assert self._result.future_id == "FGBLM26"
        assert self._result.bond_id == "DE000BU2Z049"

    def verify_carry_value(self):
        assert self._result is not None
        assert self._result.carry > 0
        assert self._result.carry == pytest.approx(0.083, abs=1e-3)
