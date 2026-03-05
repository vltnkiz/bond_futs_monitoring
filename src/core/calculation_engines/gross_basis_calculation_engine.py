from datetime import datetime, timezone

from core.calculation_engines.calculation_engine import CalculationEngine
from core.models.calculations import GrossBasisCalcInput, GrossBasisCalcResult
import logging

logger = logging.getLogger(__name__)


class GrossBasisCalculationEngine(CalculationEngine[GrossBasisCalcInput, GrossBasisCalcResult]):

    def _compute(self, i: GrossBasisCalcInput) -> GrossBasisCalcResult | None:
        try:
            futures_mid = (i.futures_bid + i.futures_ask) / 2
            bond_mid    = (i.bond_bid + i.bond_ask) / 2
            gross_basis = bond_mid - (futures_mid * i.conversion_factor)

            return GrossBasisCalcResult(
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