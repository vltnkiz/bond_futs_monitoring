from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class MonitoringRequest:
    future_id: str
    bond_ids: List[str] = field(default_factory=list)