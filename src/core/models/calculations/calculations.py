from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CalcInput:
    future_id: Optional[str]
    bond_id: Optional[str]
    input_timestamp: datetime

@dataclass(frozen=True)
class CalcResult:
    future_id: Optional[str]
    bond_id: Optional[str]
    calc_timestamp: datetime