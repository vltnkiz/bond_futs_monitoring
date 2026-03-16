from datetime import date
import numpy as np

from .rate_curve import RateCurve


class InterpolatedCurve(RateCurve):

    def __init__(self, name: str = "interpolated"):
        self._name = name
        self._tenors: dict[date, float] = {}   # date → rate, unordered
        self._sorted_days: list[int] = []       # days-from-epoch, kept in sync
        self._sorted_rates: list[float] = []    # rates, same order

    def update(self, delivery_date: date, rate: float) -> None:
        """Add or overwrite a single tenor, then re-sort."""
        self._tenors[delivery_date] = rate
        self._rebuild()

    def update_many(self, tenors: list[tuple[date, float]]) -> None:
        """Batch update — rebuilds once at the end."""
        for delivery_date, rate in tenors:
            self._tenors[delivery_date] = rate
        self._rebuild()

    def get_rate(self, delivery_date: date) -> float:
        if len(self._sorted_days) < 2:
            raise ValueError("Curve needs at least 2 tenors to interpolate")
        epoch = date(1970, 1, 1)
        date_days = (delivery_date - epoch).days
        return float(np.interp(date_days, self._sorted_days, self._sorted_rates))

    def _rebuild(self) -> None:
        epoch = date(1970, 1, 1)
        sorted_items = sorted(self._tenors.items())          # sort by date key
        self._sorted_days  = [(d - epoch).days for d, _ in sorted_items]
        self._sorted_rates = [r for _, r in sorted_items]

    @property
    def name(self) -> str:
        return self._name