from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Optional


@dataclass(frozen=True)
class Bond:
    isin: str
    coupon_rate: float
    maturity_date: date
    day_count_convention: str
    conversion_factors: Dict[str, float] = field(default_factory=dict)
    next_coupon_date: Optional[date] = None
    last_coupon_date: Optional[date] = None

    def get_conversion_factor(self, future_id: str) -> Optional[float]:
        return self.conversion_factors.get(future_id)

