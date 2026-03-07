from datetime import datetime, timezone

from .calculation_engine import CalculationEngine
from src.core.models.calculations import GrossBasisCalcInput, GrossBasisCalcResult
import logging

logger = logging.getLogger(__name__)


class GrossBasisCalculationEngine(CalculationEngine[GrossBasisCalcInput, GrossBasisCalcResult]):

    def _compute(self, i: GrossBasisCalcInput) -> GrossBasisCalcResult | None:
        try:
            futures_mid = (i.futures_bid + i.futures_ask) / 2
            bond_mid    = (i.bond_bid + i.bond_ask) / 2
            gross_basis = bond_mid - (futures_mid * i.conversion_factor)

            return GrossBasisCalcResult(
                future_id=i.future_id,
                bond_id=i.bond_id,
                calc_timestamp=datetime.now(timezone.utc),
                gross_basis=gross_basis,
                gross_basis_timestamp=datetime.now(timezone.utc),
            )
        except Exception as e:
            logger.error(f"Compute failed for {i.bond_id}: {e}")
            return None