from datetime import datetime

import pandas as pd

from static_data_loader.adapters.lseg_market_data_provider import LSEGMarketDataProvider
from static_data_loader.core.models.Bond import Bond
from static_data_loader.core.models.BondDefinition import BondDefinition
from static_data_loader.core.models.Future import Future
from static_data_loader.core.models.FutureDefinition import FutureDefinition


def convert_contract_symbol(raw_contract: str) -> str:
    """
    Example: "CONF 2026-03-06" -> "CONFH26"
    """
    month_codes = {
        1: 'F', 2: 'G', 3: 'H', 4: 'J', 5: 'K', 6: 'M',
        7: 'N', 8: 'Q', 9: 'U', 10: 'V', 11: 'X', 12: 'Z'
    }
    
    # Parse "CONF 2026-03-06" format
    parts = raw_contract.split()
    if len(parts) == 2:
        product_code = parts[0]
        date_str = parts[1]
        
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            month_letter = month_codes[date.month]
            year_2digit = date.strftime("%y")
            return f"{product_code}{month_letter}{year_2digit}"
        except (ValueError, KeyError):
            # If parsing fails, return original
            return raw_contract
    
    return raw_contract


def update_bond_definition(df: pd.DataFrame, bond_json_file: str) -> BondDefinition:
    bond_portfolio = BondDefinition(bond_json_file)
    isin_groups = df.groupby('ISIN')
    
    for isin, group in isin_groups:
        coupon_rate = group['Coupon'].iloc[0]
        maturity_date = group['Maturity'].iloc[0]
        
        if bond_portfolio.get_bond(isin):
            bond = bond_portfolio.get_bond(isin)
            print(f"  Updating: {isin}")
        else:
            bond = Bond(
                ISIN=isin,
                CouponRate=coupon_rate,
                MaturityDate=maturity_date,
                DayCountConv="ACT/ACT"
            )
            bond_portfolio.add_bond(bond)
            print(f"  Added: {isin}")
        
        for _, row in group.iterrows():
            raw_contract = row['#Contract']
            contract = convert_contract_symbol(raw_contract)
            conv_fac = row['ConvFac']
            bond.add_conversion_factor(contract, conv_fac)
    
    print(f"\nSaving {len(bond_portfolio)} bonds to {bond_json_file}...")
    bond_portfolio.save()
    
    return bond_portfolio


def update_future_definition(df: pd.DataFrame, future_json_file: str, market_data_provider: LSEGMarketDataProvider) -> FutureDefinition:
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


def update_definitions(csv_file: str, bond_json_file: str, future_json_file: str) -> tuple:
    print(f"Reading CSV: {csv_file}")
    df = pd.read_csv(csv_file, sep=";")
    
    # Update bond definitions
    bond_portfolio = update_bond_definition(df, bond_json_file)
    
    # Update future definitions
    market_data_provider = LSEGMarketDataProvider()
    future_portfolio = update_future_definition(df, future_json_file, market_data_provider)

    return bond_portfolio, future_portfolio