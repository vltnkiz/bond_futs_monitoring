from abc import ABC, abstractmethod
from typing import Callable

from src.core.models.tick import Tick
from src.core.models.calculations.gross_basis_calculations import GrossBasisCalcResult


class IGrossBasisMonitorUseCase(ABC):

    @abstractmethod
    def on_bond_tick(self, isin: str, tick: Tick) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_future_tick(self, contract_symbol: str, tick: Tick) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, callback: Callable[[GrossBasisCalcResult], None]) -> None:
        raise NotImplementedError
