import logging
from typing import Callable

from src.net_basis_monitor.adapters.market_data_feed.lseg_market_data_feed import LSEGMarketDataFeed
from src.net_basis_monitor.adapters.static_data_provider.json_static_data_provider import JsonStaticDataProvider
from src.net_basis_monitor.core.models.calculation_engines.carry_calculation_engine import CarryCalculationEngine
from src.net_basis_monitor.core.models.calculation_engines.gross_basis_calculation_engine import GrossBasisCalculationEngine
from src.net_basis_monitor.core.models.value_objects.net_basis import NetBasis
from src.net_basis_monitor.core.services.monitoring_request_builder import MonitoringRequestBuilder
from src.net_basis_monitor.core.services.net_basis_factory import NetBasisFactory
from src.net_basis_monitor.core.use_cases.monitor_net_basis import MonitorNetBasisUseCase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def build_monitor() -> tuple[MonitorNetBasisUseCase, list]:
    static_data_provider = JsonStaticDataProvider()
    gross_basis_engine = GrossBasisCalculationEngine()
    carry_engine = CarryCalculationEngine()

    future_ids = [f.isin for f in static_data_provider.get_futures()]
    requests = MonitoringRequestBuilder(static_data_provider).build(future_ids)

    factory = NetBasisFactory(
        static_data_provider=static_data_provider,
        gross_basis_engine=gross_basis_engine,
        carry_engine=carry_engine,
    )

    monitor = MonitorNetBasisUseCase(
        market_data_feed=LSEGMarketDataFeed(),
        net_basis_factory=factory,
    )

    return monitor, requests


def run(on_result: Callable[[NetBasis], None]) -> None:
    monitor, requests = build_monitor()
    monitor.subscribe(on_result)
    monitor.start(requests)


def _print_net_basis(result: NetBasis) -> None:
    print(
        f"[{result.timestamp:%Y-%m-%d %H:%M:%S}] "
        f"{result.future_id} | {result.bond_id} | "
        f"Net Basis: {result.value:+.4f}  "
        f"Gross Basis: {result.gross_basis.gross_basis:+.4f}  "
        f"Carry: {result.carry.carry:+.4f}"
    )

if __name__ == "__main__":
    run(_print_net_basis)