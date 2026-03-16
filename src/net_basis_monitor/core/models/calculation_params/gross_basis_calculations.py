from dataclasses import dataclass
from datetime import datetime

from .calculations import CalcInput, CalcResult

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
    bond_id: str
    future_id: str

@dataclass(frozen=True)
class GrossBasisCalcResult(CalcResult):
    gross_basis: float
    gross_basis_timestamp: datetime
    bond_id: str
    future_id: str