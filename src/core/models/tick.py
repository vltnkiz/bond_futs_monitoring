import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
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

    def is_bid_stale(self, max_age: datetime.timedelta) -> bool:
        if self.bid_timestamp is None:
            return True
        return datetime.datetime.now(datetime.timezone.utc) - self.bid_timestamp > max_age

    def is_ask_stale(self, max_age: datetime.timedelta) -> bool:
        if self.ask_timestamp is None:
            return True
        return datetime.datetime.now(datetime.timezone.utc) - self.ask_timestamp > max_age

    def is_stale(self, max_age: datetime.timedelta) -> bool:
        return self.is_bid_stale(max_age) or self.is_ask_stale(max_age)

    def is_stale_relative_to(self, other: "Tick", max_cross_age: datetime.timedelta) -> bool:
        if self.bid_timestamp is None or other.bid_timestamp is None:
            return True
        if self.ask_timestamp is None or other.ask_timestamp is None:
            return True
        max_seconds = max_cross_age.total_seconds()
        if abs((self.bid_timestamp - other.bid_timestamp).total_seconds()) > max_seconds:
            return True
        if abs((self.ask_timestamp - other.ask_timestamp).total_seconds()) > max_seconds:
            return True
        return False