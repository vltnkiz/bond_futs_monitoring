from abc import ABC, abstractmethod
from typing import List

from src.net_basis_monitor.core.models import Bond, Future


class StaticDataProvider(ABC):
    @abstractmethod
    def get_bonds(self) -> List[Bond]:
        raise NotImplementedError

    @abstractmethod
    def get_futures(self) -> List[Future]:
        raise NotImplementedError