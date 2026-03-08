from datetime import datetime

from .calculations import CalcInput, CalcResult

class CarryCalcInput(CalcInput):
    dirty_price: float
    coupon_rate: float
    delivery_date: datetime
    repo_rate: float
    next_coupon_date: datetime
    last_coupon_date: datetime
    coupon_income_day_convention: str = "ACT/ACT"
    financing_day_convention: str = "ACT/365"

class CarryCalcResult(CalcResult):
    carry: float
    carry_timestamp: datetime
    bond_id: str