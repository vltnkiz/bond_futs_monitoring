from datetime import datetime

from .calculations import CalcInput, CalcResult
from src.core.curves import RateCurve

class CarryCalcInput(CalcInput):
    dirty_price: float
    coupon_rate: float
    delivery_date: datetime
    rate_curve: RateCurve
    coupon_income_day_convention: str = "ACT/ACT"
    financing_day_convention: str = "ACT/365"

class CarryCalcResult(CalcResult):
    carry: float
    carry_timestamp: datetime