from dataclasses import dataclass
from datetime import datetime

from src.net_basis_monitor.core.models.calculation_params.gross_basis_calculations import GrossBasisCalcResult
from src.net_basis_monitor.core.models.calculation_params.carry_calculations import CarryCalcResult


@dataclass(frozen=True)
class NetBasis:
    future_id: str
    bond_id: str
    timestamp: datetime
    
    value: float

    gross_basis: GrossBasisCalcResult
    carry: CarryCalcResult