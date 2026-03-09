import os
from typing import Optional
import pandas as pd
import lseg.data as ld
from lseg.data.content import search
from src.core.ports.driven import StaticMarketDataProvider


class LSEGMarketDataProvider(StaticMarketDataProvider):
    def __init__(self, config_path: str = None):
        if config_path:
            os.environ["LD_LIB_CONFIG_PATH"] = config_path
        elif "LD_LIB_CONFIG_PATH" not in os.environ:
            # Try to find config in current directory
            default_path = os.path.join(os.path.dirname(__file__), "lseg-data.config.json")
            if os.path.exists(default_path):
                os.environ["LD_LIB_CONFIG_PATH"] = default_path

    def get(self, ric: str, field: str, view=None) -> Optional[str]:
        try:
            # Open LSEG session
            ld.open_session()
            
            try:
                if view is None:
                    view = search.Views.BOND_FUT_OPT_QUOTES
                # Fetch data
                response = search.Definition(
                    view=view,
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
