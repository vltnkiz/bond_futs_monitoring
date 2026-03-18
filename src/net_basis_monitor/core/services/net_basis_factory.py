import logging
from typing import List, Tuple

from src.net_basis_monitor.core.models.curves.rate_curve import RateCurve
from src.net_basis_monitor.core.models.value_objects.monitoring_request import MonitoringRequest
from src.net_basis_monitor.core.models.market_state import BondMarketState, FutureMarketState
from src.net_basis_monitor.core.models.net_basis_strategy import NetBasisStrategy
from src.net_basis_monitor.core.ports.static_data_provider import StaticDataProvider
from src.net_basis_monitor.core.services.net_basis_engine import NetBasisEngine
from src.net_basis_monitor.core.models.calculation_engines.gross_basis_calculation_engine import GrossBasisCalculationEngine
from src.net_basis_monitor.core.models.calculation_engines.carry_calculation_engine import CarryCalculationEngine

logger = logging.getLogger(__name__)

class NetBasisFactory:
    def __init__(
        self,
        static_data_provider: StaticDataProvider,
        gross_basis_engine: GrossBasisCalculationEngine,
        carry_engine: CarryCalculationEngine,
    ):
        self._static_data_provider = static_data_provider
        self._gross_basis_engine = gross_basis_engine
        self._carry_engine = carry_engine

    def create_engine(self, requests: List[MonitoringRequest]) -> Tuple[NetBasisEngine, List[str]]:
        engine = NetBasisEngine()

        bond_map = {b.isin: b for b in self._static_data_provider.get_bonds()}
        future_map = {f.contract_symbol: f for f in self._static_data_provider.get_futures()}

        instruments_to_monitor = set()
        created_states: dict = {}

        for req in requests:
            future_def = future_map.get(req.future_id)
            if not future_def:
                logger.warning(f"Future {req.future_id} not found. Skipping.")
                continue

            bond_def = bond_map.get(req.bond_id)
            if not bond_def:
                logger.warning(f"Bond {req.bond_id} not found. Skipping.")
                continue

            if req.future_id not in created_states:
                f_state = FutureMarketState(instrument=future_def)
                created_states[req.future_id] = f_state
                engine.register_state(f_state)
                instruments_to_monitor.add(f_state.instrument_id)

            if req.bond_id not in created_states:
                b_state = BondMarketState(instrument=bond_def)
                created_states[req.bond_id] = b_state
                engine.register_state(b_state)
                instruments_to_monitor.add(b_state.instrument_id)

            strategy = NetBasisStrategy(
                bond_state=created_states[req.bond_id],
                future_state=created_states[req.future_id],
                gross_basis_engine=self._gross_basis_engine,
                carry_engine=self._carry_engine
            )
            engine.register_strategy(strategy)

        return engine, list(instruments_to_monitor)