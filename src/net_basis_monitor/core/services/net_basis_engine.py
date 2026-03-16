import logging
from collections import defaultdict
from typing import Dict, List

from src.net_basis_monitor.core.models.value_objects.tick import Tick
from src.net_basis_monitor.core.models.value_objects.net_basis import NetBasis
from src.net_basis_monitor.core.models.market_state import MarketState, BondMarketState
from src.net_basis_monitor.core.models.net_basis_strategy import NetBasisStrategy

logger = logging.getLogger(__name__)

class NetBasisEngine:
    def __init__(self):
        self._states: Dict[str, MarketState] = {}
        self._routing_table: Dict[str, List[NetBasisStrategy]] = defaultdict(list)

    def register_state(self, state: MarketState) -> None:
        self._states[state.instrument_id] = state

    def register_strategy(self, strategy: NetBasisStrategy) -> None:
        self._routing_table[strategy.bond_state.instrument_id].append(strategy)
        self._routing_table[strategy.future_state.instrument_id].append(strategy)

    def process_tick(self, tick: Tick) -> List[NetBasis]:
        results = []
        
        state = self._states.get(tick.ric)
        if not state:
            return results
        
        state.on_tick(tick)

        strategies = self._routing_table.get(tick.ric, [])
        for strategy in strategies:
            result = strategy.compute()
            if result:
                results.append(result)
        
        return results

    def update_repo_rate(self, isin: str, rate: float) -> List[NetBasis]:
        results = []
        state = self._states.get(isin)
        
        if isinstance(state, BondMarketState):
            state.set_repo_rate(rate)
            
            # Recalculate dependent strategies
            strategies = self._routing_table.get(isin, [])
            for strategy in strategies:
                result = strategy.compute()
                if result:
                    results.append(result)
        else:
            logger.warning(f"Received repo rate for {isin}, but it is not monitored or not a bond.")
            
        return results