from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

CalcInput = TypeVar("CalcInput")
CalcResult = TypeVar("CalcResult")


class CalculationEngine(ABC, Generic[CalcInput, CalcResult]):

    @abstractmethod
    def compute(self, input_data: CalcInput) -> Optional[CalcResult]:
        raise NotImplementedError