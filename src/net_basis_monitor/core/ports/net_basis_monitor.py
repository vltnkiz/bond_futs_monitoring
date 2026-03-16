from abc import ABC, abstractmethod
from typing import Callable, List

from src.net_basis_monitor.core.models.value_objects.monitoring_request import MonitoringRequest
from src.net_basis_monitor.core.models.value_objects.net_basis import NetBasis


class NetBasisMonitor(ABC):
    @abstractmethod
    def start(self, instruments: List[MonitoringRequest]) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, callback: Callable[[NetBasis], None]) -> None:
        raise NotImplementedError