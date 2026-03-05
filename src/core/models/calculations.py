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

@dataclass(frozen=True)
class GrossBasisCalcInput(CalcInput):
    bond_ask: float
    bond_bid: float
    futures_bid: float
    futures_ask: float
    bond_ask_timestamp: datetime
    bond_bid_timestamp: datetime
    futures_bid_timestamp: datetime
    futures_ask_timestamp: datetime
    conversion_factor: float

@dataclass(frozen=True)
class GrossBasisCalcResult(CalcResult):
    gross_basis: float
    gross_basis_timestamp: datetime