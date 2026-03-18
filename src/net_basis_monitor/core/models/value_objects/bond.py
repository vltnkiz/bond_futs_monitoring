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

    @property
    def lseg_ric(self) -> str:
        return f"{self.isin[0:2]}{self.isin[5:11]}="

    def get_conversion_factor(self, future_contract_symbol: str) -> Optional[float]:
        return self.conversion_factors.get(future_contract_symbol)

