from typing import Callable

from src.application.services.calc_input_factories import gross_basis_calc_input_factory
from src.application.services.tick_state_store import StalenessConfig, TickStateStore
from src.core.calculation_engines.gross_basis_calculation_engine import GrossBasisCalculationEngine
from src.core.models.bond import Bond
from src.core.models.future import Future
from src.core.models.tick import Tick
from src.core.models.calculations.gross_basis_calculations import GrossBasisCalcResult
from src.core.ports.driving.gross_basis_monitor_port import IGrossBasisMonitorUseCase


class MonitorGrossBasisUseCase(IGrossBasisMonitorUseCase):

    def __init__(
        self,
        future: Future,
        bonds: list[Bond],
        engine: GrossBasisCalculationEngine,
        staleness_config: StalenessConfig | None = None,
    ) -> None:
        self._store = TickStateStore(
            future=future,
            bonds=bonds,
            calc_input_factory=gross_basis_calc_input_factory,
            staleness_config=staleness_config,
        )
        self._store.subscribe(engine.on_calc_input)
        self._engine = engine

    def on_bond_tick(self, isin: str, tick: Tick) -> None:
        self._store.update_bond(isin, tick)

    def on_future_tick(self, contract_symbol: str, tick: Tick) -> None:
        self._store.update_future(contract_symbol, tick)

    def subscribe(self, callback: Callable[[GrossBasisCalcResult], None]) -> None:
        self._engine.subscribe(callback)
