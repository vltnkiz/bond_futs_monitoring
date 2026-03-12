from typing import Callable

from src.application.services.calc_input_factories import carry_calc_input_factory
from src.application.services.repo_curve_service import RepoCurveService
from src.application.services.tick_state_store import StalenessConfig
from src.core.calculation_engines.carry_calculation_engine import CarryCalculationEngine
from src.core.models.bond import Bond
from src.core.models.future import Future
from src.core.models.tick import Tick
from src.core.models.calculations.carry_calculations import CarryCalcResult
from src.core.ports.driving.carry_monitor_port import ICarryMonitorUseCase


class MonitorCarryUseCase(ICarryMonitorUseCase):

    def __init__(
        self,
        bonds: list[Bond],
        futures: list[Future],
        repo_curve_service: RepoCurveService,
        engine: CarryCalculationEngine,
        staleness_config: StalenessConfig | None = None,
    ) -> None:
        self._bonds: dict[str, Bond] = {b.ISIN: b for b in bonds}
        self._futures: list[Future] = futures
        self._repo_curve_service = repo_curve_service
        self._engine = engine
        self._staleness_config = staleness_config or StalenessConfig()
        self._bond_ticks: dict[str, Tick] = {}

    def on_bond_tick(self, isin: str, tick: Tick) -> None:
        self._bond_ticks[isin] = tick
        self._recalc_bond(isin)

    def on_repo_tick(self, ric: str, tick: Tick) -> None:
        self._repo_curve_service.on_tick(tick)
        self._recalc_all_bonds()

    def subscribe(self, callback: Callable[[CarryCalcResult], None]) -> None:
        self._engine.subscribe(callback)

    def _recalc_bond(self, isin: str) -> None:
        tick = self._bond_ticks.get(isin)
        if tick is None or tick.bid is None or tick.ask is None:
            return
        if tick.is_stale(self._staleness_config.max_bond_quote_age):
            return
        bond = self._bonds[isin]
        for future in self._futures:
            if isin not in future.DeliverableBonds:
                continue
            try:
                calc_input = carry_calc_input_factory(bond, tick, future, self._repo_curve_service)
            except ValueError:
                continue  # curve not yet populated enough to interpolate
            self._engine.on_calc_input(calc_input)

    def _recalc_all_bonds(self) -> None:
        for isin in self._bonds:
            self._recalc_bond(isin)
