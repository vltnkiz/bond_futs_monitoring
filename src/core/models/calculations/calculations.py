from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CalcInput:
    future_id: str
    bond_id: str
    input_timestamp: datetime

@dataclass(frozen=True)
class CalcResult:
    future_id: str
    bond_id: str
    calc_timestamp: datetime