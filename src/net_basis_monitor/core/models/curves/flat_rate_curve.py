from .rate_curve import RateCurve

class FlatRateCurve(RateCurve):
    def __init__(self, rate: float, name: str = "FlatRateCurve"):
        self._rate = rate
        self._name = name

    def get_rate(self, settlement_date) -> float:
        return self._rate

    @property
    def name(self) -> str:
        return self._name