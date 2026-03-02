from dataclasses import dataclass
from datetime import datetime

@dataclass
class GrossBasisResult:
    isin: str
    gross_basis: float
    futures_mid: float
    bond_mid: float
    conversion_factor: float
    calc_timestamp: datetime
    bond_tick_ts: datetime
    futures_tick_ts: datetime


@dataclass
class BasketEntry:
    isin: str
    conversion_factor: float

@dataclass
class DeliverableBasket:
    entries: dict[str, BasketEntry]

@dataclass
class FuturesContract:
    ric: str

@dataclass
class BondState:
    isin: str
    conversion_factor: float
    bid: float | None = None
    ask: float | None = None
    bid_last_updated: datetime | None = None
    ask_last_updated: datetime | None = None    

@dataclass
class FuturesState:
    ric: str
    bid: float | None = None
    ask: float | None = None
    bid_last_updated: datetime | None = None
    ask_last_updated: datetime | None = None

@dataclass(frozen=True)
class BasisCalcInput:
    isin: str
    bond_bid: float
    bond_ask: float
    conversion_factor: float
    futures_bid: float
    futures_ask: float
    bond_tick_ts: datetime
    futures_tick_ts: datetime