from datetime import date
import pytest

from src.core.curves.interpolated_curve import InterpolatedCurve


D1 = date(2026, 3, 8)
D2 = date(2026, 9, 8)


def two_point_curve() -> InterpolatedCurve:
    c = InterpolatedCurve()
    c.update(D1, 0.02)
    c.update(D2, 0.04)
    return c


def test_exact_tenor_returns_exact_rate():
    c = two_point_curve()
    assert c.get_rate(D1) == pytest.approx(0.02)
    assert c.get_rate(D2) == pytest.approx(0.04)


def test_interpolates_between_tenors():
    c = two_point_curve()
    rate = c.get_rate(date(2026, 6, 8))
    assert 0.02 < rate < 0.04


def test_update_overwrites_existing_tenor():
    c = two_point_curve()
    c.update(D1, 0.99)
    assert c.get_rate(D1) == pytest.approx(0.99)


def test_insert_out_of_order_still_interpolates():
    c = InterpolatedCurve()
    c.update(D2, 0.04)
    c.update(D1, 0.02)
    assert 0.02 < c.get_rate(date(2026, 6, 8)) < 0.04


def test_update_many_equivalent_to_sequential_updates():
    c1 = InterpolatedCurve()
    c1.update(D1, 0.02)
    c1.update(D2, 0.04)

    c2 = InterpolatedCurve()
    c2.update_many([(D1, 0.02), (D2, 0.04)])

    assert c1.get_rate(date(2026, 6, 8)) == pytest.approx(c2.get_rate(date(2026, 6, 8)))


def test_fewer_than_two_tenors_raises():
    c = InterpolatedCurve()
    c.update(D1, 0.02)
    with pytest.raises(ValueError):
        c.get_rate(date(2026, 6, 8))


def test_empty_curve_raises():
    c = InterpolatedCurve()
    with pytest.raises(ValueError):
        c.get_rate(date(2026, 6, 8))
