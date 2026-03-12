import queue
import threading

from src.adapters.driven.lseg_market_data_feed import LSEGMarketDataFeed
from src.application.use_cases.monitor_gross_basis import MonitorGrossBasisUseCase
from src.core.calculation_engines.gross_basis_calculation_engine import GrossBasisCalculationEngine
from src.core.models.bond_definition import BondDefinition
from src.core.models.future_definition import FutureDefinition

FIELDS = ["CF_BID", "CF_ASK"]
CONTRACT_SYMBOL = "FGBLM26"


def _isin_to_ric(isin: str) -> str:
    return f"{isin[0:2]}{isin[5:11]}="


if __name__ == "__main__":
    future_def = FutureDefinition(json_file="data/portfolios/future_definition.json")
    bond_def = BondDefinition(json_file="data/portfolios/bond_definition.json")
    future = future_def.get_future(CONTRACT_SYMBOL)
    bonds = [bond_def.get_bond(isin) for isin in future.DeliverableBonds if bond_def.get_bond(isin) is not None]
    print(f"Loaded {CONTRACT_SYMBOL} with {len(bonds)} deliverable bonds")

    bond_ric_to_isin: dict[str, str] = {_isin_to_ric(b.ISIN): b.ISIN for b in bonds}
    all_instruments = [CONTRACT_SYMBOL] + sorted(bond_ric_to_isin.keys())
    print(f"Subscribing to {len(all_instruments)} instruments")

    engine = GrossBasisCalculationEngine()
    use_case = MonitorGrossBasisUseCase(future=future, bonds=bonds, engine=engine)
    use_case.subscribe(lambda r: print(f"[GB] {r.future_id} | {r.bond_id}: {r.gross_basis:.4f}"))

    tick_queue: queue.Queue = queue.Queue()
    feed = LSEGMarketDataFeed()
    feed.subscribe(instruments=all_instruments, fields=FIELDS)
    feed.start(on_tick=lambda tick: tick_queue.put(tick))

    def _consume() -> None:
        while True:
            tick = tick_queue.get()
            if tick.ric == CONTRACT_SYMBOL:
                use_case.on_future_tick(CONTRACT_SYMBOL, tick)
            elif tick.ric in bond_ric_to_isin:
                use_case.on_bond_tick(bond_ric_to_isin[tick.ric], tick)

    consumer = threading.Thread(target=_consume, daemon=True, name="gb-consumer")
    consumer.start()

    print("Gross basis monitor running. Press Ctrl+C to stop.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        feed.stop()
        print("Stopped.")