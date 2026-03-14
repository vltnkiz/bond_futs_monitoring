import json
from pathlib import Path

from src.sourcing.adapters.static_market_data_provider.stub_static_market_data_provider import StubStaticMarketDataProvider
from src.sourcing.core.use_cases.enrich_future_expiry_dates import EnrichFutureExpiryDates
from src.sourcing.core.use_cases.refresh_future_portfolio import RefreshFuturePortfolio

_CSV_CONTENT = """\
#Contract;ISIN;Coupon;Maturity;ConvFac
FGBL 2026-03-06;DE0001102580;2.5;15.08.2046;0.651234
FGBM 2026-06-08;DE0001104883;2.2;15.02.2031;0.881100
"""


def test_expiry_dates_are_enriched(tmp_path):
    eurex_dir = tmp_path / "eurex"
    portfolio_file = tmp_path / "future_definition.json"
    fixture = Fixture(
        use_case=EnrichFutureExpiryDates(
            future_portfolio=_build_portfolio(eurex_dir, portfolio_file),
            market_data_provider=StubStaticMarketDataProvider({
                ("FGBLH26", "ExpiryDate"): "2026-03-06",
            }),
        ),
        portfolio_file=portfolio_file,
    )
    fixture.verify_expiry_dates_are_enriched()


def test_delivery_date_is_two_business_days_after_expiry(tmp_path):
    eurex_dir = tmp_path / "eurex"
    portfolio_file = tmp_path / "future_definition.json"
    fixture = Fixture(
        use_case=EnrichFutureExpiryDates(
            future_portfolio=_build_portfolio(eurex_dir, portfolio_file),
            market_data_provider=StubStaticMarketDataProvider({
                # 2026-03-06 is a Friday — delivery should skip to Tuesday 2026-03-10
                ("FGBLH26", "ExpiryDate"): "2026-03-06",
            }),
        ),
        portfolio_file=portfolio_file,
    )
    fixture.verify_delivery_date_is_two_business_days_after_expiry()


def _build_portfolio(eurex_dir: Path, portfolio_file: Path):
    eurex_dir.mkdir()
    (eurex_dir / "2026-03-09_deliverable_bonds.csv").write_text(_CSV_CONTENT, encoding="utf-8")
    RefreshFuturePortfolio(eurex_data_dir=eurex_dir, portfolio_file=portfolio_file).execute()
    from src.sourcing.core.models.future_definition import FuturePortfolio
    return FuturePortfolio(str(portfolio_file))


class Fixture:
    def __init__(self, use_case: EnrichFutureExpiryDates, portfolio_file: Path):
        self._use_case = use_case
        self._portfolio_file = portfolio_file

    def verify_expiry_dates_are_enriched(self):
        self._use_case.execute()

        data = json.loads(self._portfolio_file.read_text(encoding="utf-8"))
        future = data["FGBLH26"]
        assert future["ExpiryMonth"] == "Mar-2026"
        assert future["LastTradingDate"] == "2026-03-06"

    def verify_delivery_date_is_two_business_days_after_expiry(self):
        self._use_case.execute()

        data = json.loads(self._portfolio_file.read_text(encoding="utf-8"))
        assert data["FGBLH26"]["DeliveryDate"] == "2026-03-10"
