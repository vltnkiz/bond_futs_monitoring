from datetime import datetime, timezone
import logging

from src.core.models.calculations.carry_calculations import CarryCalcInput, CarryCalcResult
from .calculation_engine import CalculationEngine

logger = logging.getLogger(__name__)

class CarryCalculationEngine(CalculationEngine):

    def _compute(self, i: CarryCalcInput) -> CarryCalcResult | None:
        try:
            today = i.input_timestamp.date()
            days_to_delivery = (i.delivery_date - today).days
            coupon_period = (i.next_coupon_date - i.last_coupon_date).days

            if i.next_coupon_date <= i.delivery_date:
                days_after_coupon = (i.delivery_date - i.next_coupon_date).days
                coupon_income = i.coupon_rate + (i.coupon_rate * days_after_coupon / coupon_period)
            else:
                coupon_income = i.coupon_rate * days_to_delivery / coupon_period

            financing_cost = i.dirty_price * i.repo_rate * days_to_delivery / 365
            
            carry = coupon_income - financing_cost

            return CarryCalcResult(
                bond_id=i.bond_id,   
                carry=carry,
                carry_timestamp=datetime.now(timezone.utc), 
            )
        except Exception as e:
            logger.error(f"Compute failed for {i.bond_id}: {e}")
            return None