from datetime import date
from src.core.curves.interpolated_curve import InterpolatedCurve

class RepoCurveService:
    def __init__(self, ric_to_tenor: dict[str, date]):
        self._ric_to_tenor = ric_to_tenor       # e.g. {"EUROND=TTKL": date(2026,3,9), ...}
        self._curve = InterpolatedCurve(name="repo")

    def on_tick(self, tick) -> None:
        tenor_date = self._ric_to_tenor.get(tick.ric)
        if tenor_date is None:
            return
        if tick.bid is None or tick.ask is None:
            return
        mid = (tick.bid + tick.ask) / 2
        self._curve.update(tenor_date, mid)

    def get_rate(self, delivery_date: date) -> float:
        return self._curve.get_rate(delivery_date)