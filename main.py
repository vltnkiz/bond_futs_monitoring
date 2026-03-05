import queue
import threading

from src.adapters.driven.lseg_market_data_feed import LSEGMarketDataFeed
from src.core.calculation_engines import GrossBasisCalcEngine

tick_queue = queue.Queue()

feed = LSEGMarketDataFeed(...)
feed.subscribe(instruments=[...], fields=[...])
feed.start(on_tick=tick_queue.put) 

store = TickStateStore(...)
engine = GrossBasisCalcEngine()
store.subscribe(engine.on_calc_input)
engine.subscribe(lambda r: print(f"{r.future_id}, {r.bond_id}, gross basis = {r.gross_basis:.4f}"))

def consume():
    while True:
        tick = tick_queue.get()
        if tick is None:        # sentinel to stop
            break
        if tick.ric == futures_ric:
            store.update_futures(tick.bid, tick.ask, tick.timestamp)
        else:
            isin = ric_to_isin[tick.ric]   # needs a mapping
            store.update_bond(isin, tick.bid, tick.ask, tick.timestamp)

consumer = threading.Thread(target=consume, daemon=True)
consumer.start()