import logging
from collections import defaultdict
from datetime import date
from typing import Dict, List, Optional

from src.net_basis_monitor.core.models.value_objects.tick import Tick
from src.net_basis_monitor.core.models.value_objects.net_basis import NetBasis
from src.net_basis_monitor.core.models.market_state import MarketState
from src.net_basis_monitor.core.models.net_basis_strategy import NetBasisStrategy
from src.net_basis_monitor.core.models.curves.rate_curve import RateCurve

logger = logging.getLogger(__name__)

class NetBasisEngine:
    def __init__(self):
        self._states: Dict[str, MarketState] = {}
        self._routing_table: Dict[str, List[NetBasisStrategy]] = defaultdict(list)
        self._all_strategies: List[NetBasisStrategy] = []
        self._repo_ric_map: Dict[str, date] = {}
        self._rate_curve: Optional[RateCurve] = None

    def configure_repo_curve(self, rate_curve: RateCurve, ric_map: Dict[str, date]) -> None:
        self._rate_curve = rate_curve
        self._repo_ric_map = ric_map

    def register_state(self, state: MarketState) -> None:
        self._states[state.instrument_id] = state

    def register_strategy(self, strategy: NetBasisStrategy) -> None:
        self._routing_table[strategy.bond_state.instrument_id].append(strategy)
        self._routing_table[strategy.future_state.instrument_id].append(strategy)
        self._all_strategies.append(strategy)

    def process_tick(self, tick: Tick) -> List[NetBasis]:
        results = []
        logger.debug("Processing tick: ric=%s bid=%s ask=%s", tick.ric, tick.bid, tick.ask)
        
        state = self._states.get(tick.ric)
        if not state:
            logger.debug("No state registered for RIC '%s'. Registered: %s", tick.ric, list(self._states.keys()))
            return results
        
        state.on_tick(tick)

        strategies = self._routing_table.get(tick.ric, [])
        for strategy in strategies:
            result = strategy.compute()
            if result:
                results.append(result)
        
        return results

    def process_repo_tick(self, ric: str, rate: float) -> List[NetBasis]:
        delivery_date = self._repo_ric_map.get(ric)
        if delivery_date is None:
            logger.warning("Received repo tick for unknown RIC '%s'", ric)
            return []

        if self._rate_curve is None:
            logger.warning("Repo curve not configured — ignoring tick for '%s'", ric)
            return []

        self._rate_curve.update(delivery_date, rate)
        logger.debug("Repo curve updated: ric=%s delivery_date=%s rate=%.4f", ric, delivery_date, rate)

        results = []
        for strategy in self._all_strategies:
            result = strategy.compute()
            if result:
                results.append(result)
        return results