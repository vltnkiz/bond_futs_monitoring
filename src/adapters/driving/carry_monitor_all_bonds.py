import json
import queue
import threading
from datetime import date

from src.adapters.driven.lseg_market_data_feed import LSEGMarketDataFeed
from src.application.services.repo_curve_service import RepoCurveService
from src.application.use_cases.monitor_carry import MonitorCarryUseCase
from src.core.calculation_engines.carry_calculation_engine import CarryCalculationEngine
from src.core.models.bond_definition import BondDefinition
from src.core.models.future_definition import FutureDefinition

FIELDS = ["CF_BID", "CF_ASK"]
REPO_CURVE_CONFIG_PATH = "data/curves/repo_curve_config.json"


def _load_repo_curve_config() -> dict[str, date]:
    with open(REPO_CURVE_CONFIG_PATH, "r") as f:
        raw: dict[str, str] = json.load(f)
    return {ric: date.fromisoformat(d) for ric, d in raw.items()}


def _isin_to_ric(isin: str) -> str:
    return f"{isin[0:2]}{isin[5:11]}="


if __name__ == "__main__":
    bond_def = BondDefinition(json_file="data/portfolios/bond_definition.json")
    future_def = FutureDefinition(json_file="data/portfolios/future_definition.json")
    all_bonds = bond_def.get_all_bonds()
    all_futures = future_def.get_all_futures()
    repo_ric_to_tenor = _load_repo_curve_config()

    print(f"Loaded {len(all_bonds)} bonds, {len(all_futures)} futures")

    bond_ric_to_isin: dict[str, str] = {_isin_to_ric(b.ISIN): b.ISIN for b in all_bonds}
    all_instruments = sorted(bond_ric_to_isin.keys()) + list(repo_ric_to_tenor.keys())
    print(
        f"Subscribing to {len(all_instruments)} instruments "
        f"({len(bond_ric_to_isin)} bonds, {len(repo_ric_to_tenor)} repo tenors)"
    )

    repo_service = RepoCurveService(ric_to_tenor=repo_ric_to_tenor)
    engine = CarryCalculationEngine()
    use_case = MonitorCarryUseCase(
        bonds=all_bonds,
        futures=all_futures,
        repo_curve_service=repo_service,
        engine=engine,
    )
    use_case.subscribe(lambda r: print(f"[CARRY] {r.future_id} | {r.bond_id}: {r.carry:.4f}"))

    tick_queue: queue.Queue = queue.Queue()
    feed = LSEGMarketDataFeed()
    feed.subscribe(instruments=all_instruments, fields=FIELDS)
    feed.start(on_tick=lambda tick: tick_queue.put(tick))

    def _consume() -> None:
        while True:
            tick = tick_queue.get()
            if tick.ric in repo_ric_to_tenor:
                use_case.on_repo_tick(tick.ric, tick)
            elif tick.ric in bond_ric_to_isin:
                use_case.on_bond_tick(bond_ric_to_isin[tick.ric], tick)

    consumer = threading.Thread(target=_consume, daemon=True, name="carry-consumer")
    consumer.start()

    print("Carry monitor running. Press Ctrl+C to stop.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        feed.stop()
        print("Stopped.")
