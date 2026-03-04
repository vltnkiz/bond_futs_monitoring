
import pandas as pd

from src.application.convert_contract_to_symbol import convert_contract_symbol
from src.core.models.bond import Bond
from src.core.models.bond_definition import BondDefinition


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