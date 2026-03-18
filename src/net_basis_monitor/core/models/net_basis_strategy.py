import logging
from typing import Optional
from datetime import datetime, timezone

from src.net_basis_monitor.core.models.curves.rate_curve import RateCurve
from src.net_basis_monitor.core.models.market_state import BondMarketState, FutureMarketState
from src.net_basis_monitor.core.models.value_objects.net_basis import NetBasis
from src.net_basis_monitor.core.models.calculation_engines.gross_basis_calculation_engine import GrossBasisCalculationEngine
from src.net_basis_monitor.core.models.calculation_engines.carry_calculation_engine import CarryCalculationEngine
from src.net_basis_monitor.core.models.calculation_params.gross_basis_calculations import GrossBasisCalcInput
from src.net_basis_monitor.core.models.calculation_params.carry_calculations import CarryCalcInput

logger = logging.getLogger(__name__)


class NetBasisStrategy:
    def __init__(
        self,
        bond_state: BondMarketState,
        future_state: FutureMarketState,
        gross_basis_engine: GrossBasisCalculationEngine,
        carry_engine: CarryCalculationEngine,
    ):
        self.bond_state = bond_state
        self.future_state = future_state
        self.gross_basis_engine = gross_basis_engine
        self.carry_engine = carry_engine

    def compute(self) -> Optional[NetBasis]:
        if not self._is_data_sufficient():
            return None

        gb_input = self._create_gross_basis_input()
        if not gb_input:
            return None
        
        gross_basis_result = self.gross_basis_engine.compute(gb_input)
        if not gross_basis_result:
            return None

        carry_input = self._create_carry_input()
        if not carry_input:
            return None
            
        carry_result = self.carry_engine.compute(carry_input)
        if not carry_result:
            return None

        net_basis_value = gross_basis_result.gross_basis - carry_result.carry

        return NetBasis(
            future_id=self.future_state.instrument.contract_symbol,
            bond_id=self.bond_state.instrument.isin,
            timestamp=datetime.now(timezone.utc),
            value=net_basis_value,
            gross_basis=gross_basis_result,
            carry=carry_result
        )

    def _is_data_sufficient(self) -> bool:
        if not self.bond_state.last_tick or not self.future_state.last_tick:
            return False
        return True

    def _create_gross_basis_input(self) -> Optional[GrossBasisCalcInput]:
        bond_tick = self.bond_state.last_tick
        future_tick = self.future_state.last_tick
        bond = self.bond_state.instrument
        future = self.future_state.instrument

        conversion_factor = bond.get_conversion_factor(future.contract_symbol)
        if conversion_factor is None:
            logger.error(f"Missing conversion factor for {bond.isin} -> {future.contract_symbol}")
            return None

        # Ensure we have all prices
        if None in (bond_tick.bid, bond_tick.ask, future_tick.bid, future_tick.ask):
            return None

        return GrossBasisCalcInput(
            future_id=future.contract_symbol,
            bond_id=bond.isin,
            input_timestamp=datetime.now(timezone.utc),
            bond_bid=bond_tick.bid,
            bond_ask=bond_tick.ask,
            futures_bid=future_tick.bid,
            futures_ask=future_tick.ask,
            bond_bid_timestamp=bond_tick.bid_timestamp or datetime.now(timezone.utc), 
            bond_ask_timestamp=bond_tick.ask_timestamp or datetime.now(timezone.utc),
            futures_bid_timestamp=future_tick.bid_timestamp or datetime.now(timezone.utc),
            futures_ask_timestamp=future_tick.ask_timestamp or datetime.now(timezone.utc),
            conversion_factor=conversion_factor
        )

    def _create_carry_input(self) -> Optional[CarryCalcInput]:
        bond = self.bond_state.instrument
        future = self.future_state.instrument
        
        # Calculate mid price using MarketState convenience method
        bond_mid_price = self.bond_state.mid_price
        if bond_mid_price is None:
            return None
        
        if bond.next_coupon_date is None or bond.last_coupon_date is None:
            logger.error(f"Missing coupon dates for {bond.isin}")
            return None

        def to_datetime(d):
            if isinstance(d, datetime): return d
            return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)

        return CarryCalcInput(
            future_id=future.contract_symbol,
            bond_id=bond.isin,
            input_timestamp=datetime.now(timezone.utc),
            clean_price=bond_mid_price,
            coupon_rate=bond.coupon_rate,
            delivery_date=future.delivery_date,
            repo_rate=4.0,  # Placeholder, should be fetched from repo curve
            next_coupon_date=to_datetime(bond.next_coupon_date),
            last_coupon_date=to_datetime(bond.last_coupon_date),
            coupon_income_day_convention=bond.day_count_convention,
            financing_day_convention="ACT/365"
        )