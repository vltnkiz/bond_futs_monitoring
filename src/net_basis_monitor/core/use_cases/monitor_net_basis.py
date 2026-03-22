import logging
from typing import Callable, List, Set

from src.net_basis_monitor.core.ports.net_basis_monitor import NetBasisMonitor
from src.net_basis_monitor.core.ports.market_data_feed import MarketDataFeed
from src.net_basis_monitor.core.models.value_objects.monitoring_request import MonitoringRequest
from src.net_basis_monitor.core.models.value_objects.net_basis import NetBasis
from src.net_basis_monitor.core.models.value_objects.tick import Tick
from src.net_basis_monitor.core.services.net_basis_engine import NetBasisEngine
from src.net_basis_monitor.core.services.net_basis_factory import NetBasisFactory

logger = logging.getLogger(__name__)


class MonitorNetBasisUseCase(NetBasisMonitor):
    def __init__(
        self,
        market_data_feed: MarketDataFeed,
        net_basis_factory: NetBasisFactory
    ):
        self._market_data_feed = market_data_feed
        self._factory = net_basis_factory
        
        self._engine: NetBasisEngine = None
        self._repo_rics: Set[str] = set()
        self._subscribers: List[Callable[[NetBasis], None]] = []

    def start(self, requests: List[MonitoringRequest]) -> None:
        self._engine, price_symbols, repo_rics = self._factory.create_engine(requests)
        self._repo_rics = set(repo_rics)

        all_symbols = price_symbols + repo_rics
        if all_symbols:
            self._market_data_feed.subscribe(all_symbols, fields=["CF_BID", "CF_ASK"])
            self._market_data_feed.start(on_tick=self._on_tick)
            logger.info(
                "Started monitoring %d price instruments and %d repo curve tenors.",
                len(price_symbols), len(repo_rics)
            )
        else:
            logger.warning("No valid instruments to monitor found.")

    def stop(self) -> None:
        self._market_data_feed.stop()
        self._engine = None
        self._repo_rics = set()

    def subscribe(self, callback: Callable[[NetBasis], None]) -> None:
        self._subscribers.append(callback)

    def _on_tick(self, tick: Tick) -> None:
        logger.debug("Processing tick: ric=%s bid=%s ask=%s", tick.ric, tick.bid, tick.ask)
        if not self._engine:
            return

        if tick.ric in self._repo_rics:
            rate = self._mid_from_tick(tick)
            if rate is not None:
                results = self._engine.process_repo_tick(tick.ric, rate)
                for result in results:
                    self._notify(result)
        else:
            results = self._engine.process_tick(tick)
            for result in results:
                self._notify(result)

    @staticmethod
    def _mid_from_tick(tick: Tick):
        if tick.mid is not None:
            return tick.mid
        if tick.bid is not None and tick.ask is not None:
            return (tick.bid + tick.ask) / 2.0
        return None

    def _notify(self, result: NetBasis) -> None:
        for sub in self._subscribers:
            try:
                sub(result)
            except Exception as e:
                logger.error(f"Subscriber error: {e}")