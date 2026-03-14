import json
from pathlib import Path

from src.sourcing.adapters.static_market_data_provider.stub_static_market_data_provider import StubStaticMarketDataProvider
from src.sourcing.core.ports import StaticMarketDataProvider
from src.sourcing.core.use_cases.enrich_bond_coupon_dates import EnrichBondCouponDates
from src.sourcing.core.use_cases.refresh_bond_portfolio import RefreshBondPortfolio

_CSV_CONTENT = """\
#Contract;ISIN;Coupon;Maturity;ConvFac
FGBL 2026-03-06;DE0001102580;2.5;15.08.2046;0.651234
FGBM 2026-03-06;IT0005580094;1.2;15.03.2031;0.881100
"""


def test_annual_coupon_dates_are_enriched(tmp_path):
    eurex_dir = tmp_path / "eurex"
    portfolio_file = tmp_path / "portfolio.json"
    fixture = Fixture(
        use_case=EnrichBondCouponDates(
            bond_portfolio=_build_portfolio(eurex_dir, portfolio_file),
            market_data_provider=StubStaticMarketDataProvider({
                ("DE110258=", "COUPN_DATE"): "2026-08-15",
            }),
        ),
        portfolio_file=portfolio_file,
    )
    fixture.verify_annual_coupon_dates_are_enriched()


def test_semi_annual_coupon_dates_are_enriched_for_italian_bonds(tmp_path):
    eurex_dir = tmp_path / "eurex"
    portfolio_file = tmp_path / "portfolio.json"
    fixture = Fixture(
        use_case=EnrichBondCouponDates(
            bond_portfolio=_build_portfolio(eurex_dir, portfolio_file),
            market_data_provider=StubStaticMarketDataProvider({
                ("IT558009=", "COUPN_DATE"): "2026-09-15",
            }),
        ),
        portfolio_file=portfolio_file,
    )
    fixture.verify_semi_annual_coupon_dates_are_enriched_for_italian_bonds()


def _build_portfolio(eurex_dir: Path, portfolio_file: Path):
    eurex_dir.mkdir()
    (eurex_dir / "2026-03-09_deliverable_bonds.csv").write_text(_CSV_CONTENT, encoding="utf-8")
    RefreshBondPortfolio(eurex_data_dir=eurex_dir, portfolio_file=portfolio_file).execute()
    from src.sourcing.core.models.bond_definition import BondPortfolio
    return BondPortfolio(str(portfolio_file))


class Fixture:
    def __init__(self, use_case: EnrichBondCouponDates, portfolio_file: Path):
        self._use_case = use_case
        self._portfolio_file = portfolio_file

    def verify_annual_coupon_dates_are_enriched(self):
        self._use_case.execute()

        data = json.loads(self._portfolio_file.read_text(encoding="utf-8"))
        bond = data["DE0001102580"]
        assert bond["NextCouponDate"] == "2026-08-15"
        assert bond["LastCouponDate"] == "2025-08-15"

    def verify_semi_annual_coupon_dates_are_enriched_for_italian_bonds(self):
        self._use_case.execute()

        data = json.loads(self._portfolio_file.read_text(encoding="utf-8"))
        bond = data["IT0005580094"]
        assert bond["NextCouponDate"] == "2026-09-15"
        assert bond["LastCouponDate"] == "2026-03-15"
