import logging
from typing import Callable, List

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
        self._subscribers: List[Callable[[NetBasis], None]] = []

    def start(self, requests: List[MonitoringRequest]) -> None:
        self._engine, symbols = self._factory.create_engine(requests)
        
        if symbols:
            self._market_data_feed.subscribe(symbols, fields=["CF_BID", "CF_ASK"])
            self._market_data_feed.start(on_tick=self._on_tick)
            logger.info(f"Started monitoring {len(symbols)} instruments.")
        else:
            logger.warning("No valid instruments to monitor found.")

    def stop(self) -> None:
        self._market_data_feed.stop()
        self._engine = None

    def subscribe(self, callback: Callable[[NetBasis], None]) -> None:
        self._subscribers.append(callback)

    def _on_tick(self, tick: Tick) -> None:
        logger.debug("Processing tick: ric=%s bid=%s ask=%s", tick.ric, tick.bid, tick.ask)
        if self._engine:
            results = self._engine.process_tick(tick)
            for result in results:
                self._notify(result)

    def _notify(self, result: NetBasis) -> None:
        for sub in self._subscribers:
            try:
                sub(result)
            except Exception as e:
                logger.error(f"Subscriber error: {e}")

    def update_repo_rate(self, isin: str, rate: float) -> None:
        if self._engine:
            results = self._engine.update_repo_rate(isin, rate)
            for result in results:
                self._notify(result)