from dataclasses import dataclass


@dataclass(frozen=True)
class MonitoringRequest:
    future_id: str
    bond_id: str