from datetime import datetime, timezone
from typing import Callable

from calculation_engine.models import GrossBasisResult
from .tick_state_storage import BasisCalcInput
import logging

logger = logging.getLogger(__name__)

class GrossBasisEngine:
    def __init__(self):
        self._callbacks: list[Callable[[GrossBasisResult], None]] = []

    def subscribe(self, cb: Callable[[GrossBasisResult], None]) -> None:
        self._callbacks.append(cb)

    def on_calc_input(self, input: BasisCalcInput) -> None:
        result = self._compute(input)
        if result:
            self._emit(result)

    def _compute(self, i: BasisCalcInput) -> GrossBasisResult | None:
        try:
            futures_mid = (i.futures_bid + i.futures_ask) / 2
            bond_mid    = (i.bond_bid + i.bond_ask) / 2
            gross_basis = bond_mid - (futures_mid * i.conversion_factor)

            return GrossBasisResult(
                isin=i.isin,
                gross_basis=gross_basis,
                futures_mid=futures_mid,
                bond_mid=bond_mid,
                conversion_factor=i.conversion_factor,
                calc_timestamp=datetime.now(timezone.utc),
                bond_tick_ts=i.bond_tick_ts,
                futures_tick_ts=i.futures_tick_ts,
            )
        except Exception as e:
            logger.error(f"Compute failed for {i.isin}: {e}")
            return None

    def _emit(self, result: GrossBasisResult) -> None:
        for cb in self._callbacks:
            try:
                cb(result)
            except Exception as e:
                logger.error(f"Callback raised: {e}")