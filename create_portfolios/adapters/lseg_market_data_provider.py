import os
from typing import Optional
import pandas as pd
import lseg.data as ld
from lseg.data.content import search
from create_portfolios.core.ports.market_data_provider import MarketDataProvider


class LSEGMarketDataProvider(MarketDataProvider):
    def __init__(self, config_path: str = None):
        if config_path:
            os.environ["LD_LIB_CONFIG_PATH"] = config_path
        elif "LD_LIB_CONFIG_PATH" not in os.environ:
            # Try to find config in current directory
            default_path = os.path.join(os.path.dirname(__file__), "lseg-data.config.json")
            if os.path.exists(default_path):
                os.environ["LD_LIB_CONFIG_PATH"] = default_path

    def get(self, ric: str, field: str) -> Optional[str]:
        try:
            # Open LSEG session
            ld.open_session()
            
            try:
                # Fetch data
                response = search.Definition(
                    view=search.Views.BOND_FUT_OPT_QUOTES,
                    select=f"RIC,{field}",
                    filter=f"RIC eq '{ric}'",
                    top=1
                ).get_data()
                
                df = pd.DataFrame(response.data.df)
                
                if df.empty:
                    return None
                
                value = df[field].iloc[0]
                return str(value) if value is not None else None
                
            finally:
                ld.close_session()
                
        except Exception as e:
            print(f"Error retrieving {field} for RIC {ric} from LSEG: {e}")
            return None
