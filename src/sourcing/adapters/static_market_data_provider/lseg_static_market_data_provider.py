import logging
import os
from typing import Optional
import lseg.data as ld
from lseg.data.content import search
from src.sourcing.core.ports import StaticMarketDataProvider

_logger = logging.getLogger(__name__)


class LSEGStaticMarketDataProvider(StaticMarketDataProvider):
    def __init__(self, config_path: str = None):
        if config_path:
            os.environ["LD_LIB_CONFIG_PATH"] = config_path
        elif "LD_LIB_CONFIG_PATH" not in os.environ:
            default_path = os.path.join(os.path.dirname(__file__), "lseg-data.config.json")
            if os.path.exists(default_path):
                os.environ["LD_LIB_CONFIG_PATH"] = default_path

    def __enter__(self):
        ld.open_session()
        return self

    def __exit__(self, *_):
        ld.close_session()

    def get(self, ric: str, field: str, view=None) -> Optional[str]:
        try:
            if view is None:
                view = search.Views.BOND_FUT_OPT_QUOTES
            response = search.Definition(
                view=view,
                select=f"RIC,{field}",
                filter=f"RIC eq '{ric}'",
                top=1,
            ).get_data()

            hits = (response.data.raw or {}).get("Hits", [])
            if not hits:
                return None

            value = hits[0].get(field)
            return str(value) if value is not None else None

        except Exception as e:
            _logger.error("Error retrieving %s for RIC %s from LSEG: %s", field, ric, e)
            return None

