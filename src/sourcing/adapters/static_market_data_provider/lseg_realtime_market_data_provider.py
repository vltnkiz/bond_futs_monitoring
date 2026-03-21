import logging
import os
import time
from typing import Optional

import lseg.data as ld
from lseg.data.content import pricing

from src.sourcing.core.ports import MarketDataProvider

_logger = logging.getLogger(__name__)

_SNAPSHOT_TIMEOUT_S = 5


class LSEGRealtimeMarketDataProvider(MarketDataProvider):
    def __init__(self, config_path: str = None):
        if config_path:
            os.environ["LD_LIB_CONFIG_PATH"] = config_path
        elif "LD_LIB_CONFIG_PATH" not in os.environ:
            default_path = os.path.join(os.path.dirname(__file__), "lseg-data.config.json")
            if os.path.exists(default_path):
                os.environ["LD_LIB_CONFIG_PATH"] = default_path
        self._streams: list = []

    def __enter__(self):
        ld.open_session()
        return self

    def __exit__(self, *_):
        ld.close_session()

    def get(self, ric: str, field: str) -> Optional[str]:
        result: dict = {}

        try:
            stream = pricing.Definition(
                universe=[ric],
                fields=[field],
            ).get_stream()

            stream.on_refresh(lambda fields, instrument, _stream: result.update({instrument: fields}))
            stream.open(with_updates=False)

            deadline = time.time() + _SNAPSHOT_TIMEOUT_S
            while ric not in result and time.time() < deadline:
                time.sleep(0.05)

            self._streams.append(stream)
        except Exception as e:
            _logger.error("Error retrieving %s for RIC %s from LSEG real-time: %s", field, ric, e)
            return None

        fields = result.get(ric)
        if fields is None:
            _logger.warning("No snapshot received for RIC %s", ric)
            return None

        value = fields.get(field)
        return str(value) if value is not None else None

    def close(self) -> None:
        for stream in self._streams:
            try:
                stream.close()
            except Exception as e:
                _logger.warning("Error closing stream: %s", e)
        self._streams.clear()
