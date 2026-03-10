from dataclasses import dataclass
from datetime import date, datetime

from .calculations import CalcInput, CalcResult


@dataclass(frozen=True)
class CarryCalcInput(CalcInput):
    clean_price: float
    coupon_rate: float
    delivery_date: date
    repo_rate: float
    next_coupon_date: datetime
    last_coupon_date: datetime
    coupon_income_day_convention: str = "ACT/ACT"
    financing_day_convention: str = "ACT/365"


@dataclass(frozen=True)
class CarryCalcResult(CalcResult):
    carry: float