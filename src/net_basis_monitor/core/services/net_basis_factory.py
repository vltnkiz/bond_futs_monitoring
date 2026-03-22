import json
import logging
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

from src.net_basis_monitor.core.models.curves.interpolated_curve import InterpolatedCurve
from src.net_basis_monitor.core.models.curves.tenor_date_resolver import TenorDateResolver
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
        repo_curve_config: Dict[str, str],
    ):
        self._static_data_provider = static_data_provider
        self._gross_basis_engine = gross_basis_engine
        self._carry_engine = carry_engine
        # Values may be ISO date strings ("2026-03-24") or tenor labels ("ON", "1W", "3M").
        self._repo_ric_map: Dict[str, date] = {}
        resolver = TenorDateResolver()
        today = date.today()
        for ric, value in repo_curve_config.items():
            try:
                self._repo_ric_map[ric] = date.fromisoformat(value)
            except ValueError:
                try:
                    resolved = resolver.resolve(value, today)
                    self._repo_ric_map[ric] = resolved
                    logger.debug("Tenor '%s' for RIC '%s' resolved to %s", value, ric, resolved)
                except ValueError:
                    logger.warning("Unrecognised tenor or date '%s' for RIC '%s' — skipping", value, ric)

    def create_engine(self, requests: List[MonitoringRequest]) -> Tuple[NetBasisEngine, List[str], List[str]]:
        """
        Returns (engine, price_symbols, repo_rics).
        price_symbols: RICs for bond/future price subscriptions.
        repo_rics: RICs for repo curve tenor subscriptions.
        """
        engine = NetBasisEngine()
        rate_curve = InterpolatedCurve(name="repo_curve")
        engine.configure_repo_curve(rate_curve, self._repo_ric_map)

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
                carry_engine=self._carry_engine,
                rate_curve=rate_curve,
            )
            engine.register_strategy(strategy)

        return engine, list(instruments_to_monitor), list(self._repo_ric_map.keys())