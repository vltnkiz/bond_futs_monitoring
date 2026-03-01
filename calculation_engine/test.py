from datetime import datetime, timezone

from calculation_engine.gross_basis_calculation_engine import (
    GrossBasisEngine,
)
from calculation_engine.tick_state_storage import (
    BasketEntry,
    DeliverableBasket,
    FuturesContract,
    TickStateStore,
)

if __name__ == "__main__":
    basket  = DeliverableBasket(entries={
        "DE0001102481": BasketEntry(isin="DE0001102481", conversion_factor=0.7234),
        "DE0001102572": BasketEntry(isin="DE0001102572", conversion_factor=0.8012),
    })
    futures = FuturesContract(ric="FGBLc1")

    store  = TickStateStore(basket, futures)
    engine = GrossBasisEngine()
    store.subscribe(engine.on_calc_input)

    # wire a consumer
    engine.subscribe(lambda r: print(f"{r.isin} gross basis: {r.gross_basis:.4f}"))

    # simulate incoming ticks
    store.update_futures(bid=132.50, ask=132.51, ts=datetime.now(timezone.utc))
    store.update_bond("DE0001102481", bid=95.20, ask=95.22, ts=datetime.now(timezone.utc))
    store.update_bond("DE0001102481", bid=97.20, ask=95.22, ts=datetime.now(timezone.utc))