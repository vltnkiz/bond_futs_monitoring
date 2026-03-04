import pandas as pd


from src.application.convert_contract_to_symbol import convert_contract_symbol
from src.core.models.future import Future
from src.core.models.future_definition import FutureDefinition
from src.core.ports.driven import StaticMarketDataProvider

def update_future_definition(df: pd.DataFrame, future_json_file: str, market_data_provider: StaticMarketDataProvider) -> FutureDefinition:
    future_portfolio = FutureDefinition(future_json_file)
    contracts = df['#Contract'].unique()
    
    print(f"Processing {len(contracts)} contracts...")
    for raw_contract in sorted(contracts):
        contract = convert_contract_symbol(raw_contract)
        contract_bonds = df[df['#Contract'] == raw_contract]['ISIN'].unique()
        
        if future_portfolio.get_future(contract):
            future = future_portfolio.get_future(contract)
            print(f"  Updating: {contract}")
        else:
            print(f"  Fetching LSEG data for {contract}...")
            expiry_date_str = market_data_provider.get(contract, "ExpiryDate")
            
            expiry_month = ""
            delivery_date_str = ""
            
            if expiry_date_str:
                expiry_date = pd.to_datetime(expiry_date_str)
                expiry_month = expiry_date.strftime("%b-%Y")
                delivery_date = expiry_date + pd.offsets.BDay(2)
                delivery_date_str = delivery_date.strftime("%Y-%m-%d")
            
            notional_value = 100000 if contract.startswith("FGBL") else 0.0
            tick_value = 10 if contract.startswith("FGBL") else 0.0
            
            future = Future(
                ContractSymbol=contract,
                ExpiryMonth=expiry_month,
                LastTradingDate=expiry_date_str,
                DeliveryDate=delivery_date_str,
                NotionalValue=notional_value,
                TickValue=tick_value,
                NotionalCoupon=6.0,
                DeliverableBonds=set()
            )
            future_portfolio.add_future(future)
            print(f"  Added: {contract} | ExpiryDate: {expiry_date_str} | DeliveryDate: {delivery_date_str}")
        
        for isin in contract_bonds:
            if not future.is_deliverable_bond(isin):
                future.add_deliverable_bond(isin)
    
    print(f"\nSaving {len(future_portfolio)} futures to {future_json_file}...")
    future_portfolio.save()
    
    return future_portfolio