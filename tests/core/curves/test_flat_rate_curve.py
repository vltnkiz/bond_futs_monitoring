from datetime import date
import pytest

from src.core.curves.flat_rate_curve import FlatRateCurve


@pytest.mark.parametrize("rate", [0.0, 0.025, 0.10, -0.005])
def test_returns_same_rate_for_any_date(rate):
    curve = FlatRateCurve(rate)
    assert curve.get_rate(date(2026, 3, 8))  == pytest.approx(rate)
    assert curve.get_rate(date(2026, 6, 10)) == pytest.approx(rate)
    assert curve.get_rate(date(2027, 12, 31)) == pytest.approx(rate)


def test_default_name():
    curve = FlatRateCurve(0.025)
    assert curve.name == "FlatRateCurve"


def test_custom_name():
    curve = FlatRateCurve(0.025, name="my_flat_curve")
    assert curve.name == "my_flat_curve"
