from typing import List
from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Future:
    isin: str
    contract_symbol: str
    expiry_month: str
    last_trading_date: date
    delivery_date: date
    notional_value: float
    tick_value: float
    notional_coupon: float
    deliverable_bonds: List[str] = field(default_factory=list)