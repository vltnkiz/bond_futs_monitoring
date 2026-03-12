from abc import ABC, abstractmethod
from typing import Callable

from src.core.models.tick import Tick
from src.core.models.calculations.carry_calculations import CarryCalcResult


class ICarryMonitorUseCase(ABC):

    @abstractmethod
    def on_bond_tick(self, isin: str, tick: Tick) -> None: 
        raise NotImplementedError

    @abstractmethod
    def on_repo_tick(self, ric: str, tick: Tick) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, callback: Callable[[CarryCalcResult], None]) -> None:
        raise NotImplementedError
