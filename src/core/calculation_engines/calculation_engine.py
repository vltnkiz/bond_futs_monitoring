from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Callable
import logging

logger = logging.getLogger(__name__)

CalcInput = TypeVar("CalcInput")
CalcResult = TypeVar("CalcResult")


class CalculationEngine(ABC, Generic[CalcInput, CalcResult]):

    def __init__(self):
        self._callbacks: list[Callable[[CalcResult], None]] = []

    def subscribe(self, cb: Callable[[CalcResult], None]) -> None:
        self._callbacks.append(cb)

    def on_calc_input(self, input: CalcInput) -> None:
        result = self._compute(input)
        if result is not None:
            self._emit(result)

    @abstractmethod
    def _compute(self, input: CalcInput) -> CalcResult | None:
        raise NotImplementedError

    def _emit(self, result: CalcResult) -> None:
        for cb in self._callbacks:
            try:
                cb(result)
            except Exception as e:
                logger.error(f"Callback raised: {e}")