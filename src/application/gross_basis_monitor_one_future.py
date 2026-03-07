import json
import queue
import threading

from src.adapters.driven.lseg_market_data_feed import LSEGMarketDataFeed
from src.application.tick_state_store import TickStateStore
from src.application.calc_input_factories import gross_basis_calc_input_factory
from src.core.calculation_engines import GrossBasisCalculationEngine
from src.core.models.bond import Bond
from src.core.models.future import Future


def load_fgblm26_deliverable_basket() -> tuple[Future, list[Bond]]:
    with open('data/portfolios/future_definition.json', 'r') as f:
        future_def = json.load(f)
    with open('data/portfolios/bond_definition.json', 'r') as f:
        bond_def = json.load(f)

    fgblm26_data = future_def['FGBLM26']
    future = Future(
        ContractSymbol=fgblm26_data['ContractSymbol'],
        ExpiryMonth=fgblm26_data['ExpiryMonth'],
        LastTradingDate=fgblm26_data['LastTradingDate'],
        DeliveryDate=fgblm26_data['DeliveryDate'],
        NotionalValue=fgblm26_data['NotionalValue'],
        TickValue=fgblm26_data['TickValue'],
        NotionalCoupon=fgblm26_data['NotionalCoupon'],
        DeliverableBonds=set(fgblm26_data['DeliverableBonds']),
    )

    bonds = []
    for isin in fgblm26_data['DeliverableBonds']:
        if isin in bond_def:
            d = bond_def[isin]
            bonds.append(Bond(
                ISIN=d['ISIN'],
                CouponRate=d['CouponRate'],
                MaturityDate=d['MaturityDate'],
                DayCountConv=d['DayCountConv'],
                CF=d.get('CF', {}),
            ))

    return future, bonds
    
    
if __name__ == "__main__":
    future_ric = 'FGBLM26'
    future, bonds = load_fgblm26_deliverable_basket()

    tick_queue = queue.Queue()
    feed = LSEGMarketDataFeed()
    bond_rics = [f"{bond.ISIN[0:2]}{bond.ISIN[5:11]}=" for bond in bonds]
    ric_to_isin = {f"{bond.ISIN[0:2]}{bond.ISIN[5:11]}=": bond.ISIN for bond in bonds}
    feed.subscribe(instruments=[future_ric] + bond_rics, fields=['CF_BID', 'CF_ASK'])
    
    def on_tick(tick):
        print(f"Tick received: {tick}")
        tick_queue.put(tick)
    
    feed.start(on_tick=on_tick)

    store = TickStateStore(future, bonds, calc_input_factory=gross_basis_calc_input_factory)
    engine = GrossBasisCalculationEngine()
    store.subscribe(engine.on_calc_input)
    engine.subscribe(lambda r: print(f"{r.future_id}, {r.bond_id}, gross basis = {r.gross_basis:.4f}"))
    
    def consume():
        while True:
            tick = tick_queue.get()
            if tick.ric == future_ric:
                store.update_future(tick)
            else:
                isin = ric_to_isin.get(tick.ric)
                if isin:
                    tick.ric = isin
                    store.update_bond(tick)

    consumer = threading.Thread(target=consume, daemon=True)
    consumer.start()