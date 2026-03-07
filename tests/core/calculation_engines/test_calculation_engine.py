from datetime import datetime, timezone

import pytest

from src.core.calculation_engines.calculation_engine import CalculationEngine
from src.core.models.calculations import CalcInput, CalcResult

class _EchoEngine(CalculationEngine[int, int]):
    def _compute(self, input: int) -> int | None:
        return input

class _NoneEngine(CalculationEngine[int, int]):
    """Always returns None — simulates a calc that produces no result."""
    def _compute(self, input: int) -> int | None:
        return None


class _StructuredEngine(CalculationEngine[CalcInput, CalcResult]):
    """Echoes a CalcResult preserving IDs and stamping UTC time."""
    def _compute(self, input: CalcInput) -> CalcResult | None:
        return CalcResult(
            future_id=input.future_id,
            bond_id=input.bond_id,
            calc_timestamp=datetime.now(timezone.utc),
        )


_SAMPLE_INPUT = CalcInput(
    future_id="FGBL Jun26",
    bond_id="DE0001102614",
    input_timestamp=datetime(2026, 3, 7, 12, 0, 0, tzinfo=timezone.utc),
)


class TestCalculationEngineResultContract:
    """Contracts every CalcResult must satisfy, regardless of engine."""

    def setup_method(self):
        self.engine = _StructuredEngine()

    def test_result_ids_match_input(self):
        result = self.engine._compute(_SAMPLE_INPUT)
        assert result is not None
        assert result.future_id == _SAMPLE_INPUT.future_id
        assert result.bond_id == _SAMPLE_INPUT.bond_id

    def test_result_is_immutable(self):
        result = self.engine._compute(_SAMPLE_INPUT)
        assert result is not None
        with pytest.raises((AttributeError, TypeError)):
            result.future_id = "other"  # type: ignore[misc]

    def test_result_has_utc_timestamp(self):
        result = self.engine._compute(_SAMPLE_INPUT)
        assert result is not None
        assert result.calc_timestamp.tzinfo is not None


class TestCalculationEngineSubscriberPipeline:

    def setup_method(self):
        self.engine = _EchoEngine()
        self.received: list[int] = []
        self.engine.subscribe(self.received.append)

    def test_subscriber_receives_result(self):
        self.engine.on_calc_input(42)
        assert self.received == [42]

    def test_multiple_subscribers_all_notified(self):
        second: list[int] = []
        self.engine.subscribe(second.append)
        self.engine.on_calc_input(7)
        assert self.received == [7]
        assert second == [7]

    def test_no_emit_when_compute_returns_none(self):
        engine = _NoneEngine()
        results: list[int] = []
        engine.subscribe(results.append)
        engine.on_calc_input(99)
        assert results == []

    def test_faulty_subscriber_does_not_prevent_others(self):
        def bad_cb(_):
            raise RuntimeError("subscriber blew up")

        good: list[int] = []
        self.engine.subscribe(bad_cb)
        self.engine.subscribe(good.append)
        self.engine.on_calc_input(1)
        assert good == [1]

    def test_subscribers_called_in_registration_order(self):
        order: list[str] = []
        self.engine.subscribe(lambda _: order.append("second"))
        self.engine.subscribe(lambda _: order.append("third"))
        self.engine.on_calc_input(0)
        assert order == ["second", "third"]