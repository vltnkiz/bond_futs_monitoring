from dataclasses import dataclass

@dataclass(frozen=True)
class GrossBasisCalcInput:
    bond_price: float
    futures_price: float
    conversion_factor: float

@dataclass(frozen=True)
class GrossBasisCalcResult:
    gross_basis: float