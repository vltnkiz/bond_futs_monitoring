import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Tick:
    ric: str
    mid: Optional[float]
    bid: Optional[float]
    ask: Optional[float]
    bidsize: Optional[int]
    asksize: Optional[int] 
    timestamp: datetime.datetime
    is_snapshot: bool = False
    raw: dict = None