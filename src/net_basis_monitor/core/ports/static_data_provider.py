from abc import ABC, abstractmethod
from typing import List, Tuple

from src.net_basis_monitor.core.models import Bond, Future


class StaticDataProvider(ABC):
    @abstractmethod
    def get_bonds(self, isins: List[str]) -> List[Bond]:
        raise NotImplementedError

    @abstractmethod
    def get_futures(self, contract_symbols: List[str]) -> List[Future]:
        raise NotImplementedError

    def get_instruments(self, bond_isins: List[str], future_ids: List[str]) -> Tuple[List[Bond], List[Future]]:
        return self.get_bonds(bond_isins), self.get_futures(future_ids)