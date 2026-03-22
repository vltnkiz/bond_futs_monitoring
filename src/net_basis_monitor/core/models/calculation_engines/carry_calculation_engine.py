from datetime import datetime, timedelta, timezone
import logging

from src.net_basis_monitor.core.models.calculation_params.carry_calculations import CarryCalcInput, CarryCalcResult
from .calculation_engine import CalculationEngine

logger = logging.getLogger(__name__)

class CarryCalculationEngine(CalculationEngine[CarryCalcInput, CarryCalcResult]):

    def compute(self, i: CarryCalcInput) -> CarryCalcResult | None:
        try:
            settlement = i.settlement_date
            next_coupon = i.next_coupon_date.date()
            last_coupon = i.last_coupon_date.date()

            days_to_delivery = (i.delivery_date - i.input_timestamp.date()).days
            coupon_period = 365
            
            if coupon_period <= 0:
                 logger.warning(f"Invalid coupon period {coupon_period} for {i.bond_id}")
                 return None

            days_since_last_coupon = (settlement - last_coupon).days
            accrued = i.coupon_rate * days_since_last_coupon / coupon_period
            dirty_price = i.clean_price + accrued

            if next_coupon <= i.delivery_date:
                days_after_coupon = (i.delivery_date - next_coupon).days
                coupon_income = i.coupon_rate + (i.coupon_rate * days_after_coupon / coupon_period)
            else:
                coupon_income = i.coupon_rate * days_to_delivery / coupon_period

            financing_cost = dirty_price * (i.repo_rate / 100) * days_to_delivery / 360

            carry = coupon_income - financing_cost

            logger.info(
                f"Carry [{i.bond_id} / {i.future_id}] | "
                f"settlement={settlement} | delivery={i.delivery_date} | next_coupon={next_coupon} | last_coupon={last_coupon} | "
                f"days_since_last_coupon={days_since_last_coupon} | days_to_delivery={days_to_delivery} | coupon_period={coupon_period} | "
                f"clean={i.clean_price:.4f} accrued={accrued:.4f} dirty={dirty_price:.4f} | "
                f"coupon_income={coupon_income:.4f} financing={financing_cost:.4f} (repo={i.repo_rate:.4f}%) | "
                f"carry={carry:.4f}"
            )

            return CarryCalcResult(
                future_id=i.future_id,
                bond_id=i.bond_id,
                carry=carry,
                calc_timestamp=datetime.now(timezone.utc),
            )
        except Exception as e:
            logger.error(f"Carry compute failed for {i.bond_id}: {e}")
            return None