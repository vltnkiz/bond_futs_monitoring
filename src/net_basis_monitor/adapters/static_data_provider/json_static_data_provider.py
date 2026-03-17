import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from src.net_basis_monitor.core.models import Bond, Future
from src.net_basis_monitor.core.ports.static_data_provider import StaticDataProvider


_PROJECT_ROOT = Path(__file__).parents[4]
_DEFAULT_BOND_PATH = _PROJECT_ROOT / "data" / "portfolios" / "bond_portfolio.json"
_DEFAULT_FUTURE_PATH = _PROJECT_ROOT / "data" / "portfolios" / "future_definition.json"


class JsonStaticDataProvider(StaticDataProvider):
    def __init__(
        self,
        bond_portfolio_path: str | Path = _DEFAULT_BOND_PATH,
        future_definition_path: str | Path = _DEFAULT_FUTURE_PATH,
    ):
        self._bonds: Dict[str, Bond] = {}
        self._futures: Dict[str, Future] = {}
        self._load_bonds(Path(bond_portfolio_path))
        self._load_futures(Path(future_definition_path))


    def _load_bonds(self, path: Path) -> None:
        with open(path, "r") as f:
            data = json.load(f)
        for isin, entry in data.items():
            self._bonds[isin] = Bond(
                isin=entry["ISIN"],
                coupon_rate=entry["CouponRate"],
                maturity_date=datetime.strptime(entry["MaturityDate"], "%d.%m.%Y").date(),
                day_count_convention=entry["DayCountConv"],
                conversion_factors=entry.get("CF", {}),
            )

    def _load_futures(self, path: Path) -> None:
        with open(path, "r") as f:
            data = json.load(f)
        for symbol, entry in data.items():
            self._futures[symbol] = Future(
                isin=entry["ContractSymbol"],
                contract_symbol=entry["ContractSymbol"],
                expiry_month=entry["ExpiryMonth"],
                last_trading_date=datetime.strptime(entry["LastTradingDate"], "%Y-%m-%d").date(),
                delivery_date=datetime.strptime(entry["DeliveryDate"], "%Y-%m-%d").date(),
                notional_value=entry["NotionalValue"],
                tick_value=entry["TickValue"],
                notional_coupon=entry["NotionalCoupon"],
                deliverable_bonds=entry.get("DeliverableBonds", []),
            )

    def get_bonds(self, isins: List[str]) -> List[Bond]:
        return [self._bonds[isin] for isin in isins if isin in self._bonds]

    def get_futures(self, contract_symbols: List[str]) -> List[Future]:
        return [self._futures[symbol] for symbol in contract_symbols if symbol in self._futures]