import datetime
from dataclasses import dataclass, field
from typing import Callable, Optional, TypeAlias


@dataclass
class Tick:
    ric: str
    mid: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_timestamp: Optional[datetime.datetime] = None
    ask_timestamp: Optional[datetime.datetime] = None
    bidsize: Optional[int] = None
    asksize: Optional[int] = None
    timestamp: Optional[datetime.datetime] = None
    is_snapshot: bool = False
    raw: Optional[dict] = field(default=None, hash=False, compare=False)


TickHandler: TypeAlias = Callable[[Tick], None]