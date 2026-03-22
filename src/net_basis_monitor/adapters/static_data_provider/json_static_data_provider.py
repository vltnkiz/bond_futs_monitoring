import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional

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
        isin_prefix: Optional[str] = None,
    ):
        self._bonds: Dict[str, Bond] = {}
        self._futures: Dict[str, Future] = {}
        self._isin_prefix = isin_prefix
        self._load_bonds(Path(bond_portfolio_path))
        self._load_futures(Path(future_definition_path))


    @staticmethod
    def _parse_date(value: Optional[str]) -> Optional[date]:
        if not value:
            return None
        return date.fromisoformat(str(value)[:10])

    def _load_bonds(self, path: Path) -> None:
        with open(path, "r") as f:
            data = json.load(f)
        for isin, entry in data.items():
            if self._isin_prefix and not entry["ISIN"].startswith(self._isin_prefix):
                continue
            self._bonds[isin] = Bond(
                isin=entry["ISIN"],
                coupon_rate=entry["CouponRate"],
                maturity_date=datetime.strptime(entry["MaturityDate"], "%d.%m.%Y").date(),
                day_count_convention=entry["DayCountConv"],
                conversion_factors=entry.get("CF", {}),
                next_coupon_date=self._parse_date(entry["NextCouponDate"]),
                last_coupon_date=self._parse_date(entry["LastCouponDate"]),
            )

    def _load_futures(self, path: Path) -> None:
        with open(path, "r") as f:
            data = json.load(f)
        for symbol, entry in data.items():
            if self._isin_prefix:
                deliverable = entry.get("DeliverableBonds", [])
                if not any(b.startswith(self._isin_prefix) for b in deliverable):
                    continue
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

    def get_bonds(self) -> List[Bond]:
        return list(self._bonds.values())

    def get_futures(self) -> List[Future]:
        return list(self._futures.values())