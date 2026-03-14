import json
from pathlib import Path

import pytest

from src.sourcing.core.use_cases.refresh_bond_portfolio import RefreshBondPortfolio

_CSV_CONTENT = """\
#Contract;ISIN;Coupon;Maturity;ConvFac
FGBL 2026-03-06;DE0001102580;2.5;15.08.2046;0.651234
FGBL 2026-06-08;DE0001102580;2.5;15.08.2046;0.654321
FGBM 2026-03-06;DE0001104883;2.2;15.02.2031;0.881100
FGBM 2026-06-08;DE0001104883;2.2;15.02.2031;0.884500
"""


def test_bonds_are_saved_to_portfolio(tmp_path):
    fixture = Fixture(tmp_path=tmp_path)
    fixture.verify_bonds_are_saved_to_portfolio()


def test_existing_bond_conversion_factors_are_updated(tmp_path):
    old_portfolio = {
        "DE0001102580": {
            "ISIN": "DE0001102580",
            "CouponRate": 2.5,
            "MaturityDate": "15.08.2046",
            "DayCountConv": "ACT/ACT",
            "CF": {"FGBLH26": 0.999999},
        }
    }
    (tmp_path / "portfolio.json").write_text(json.dumps(old_portfolio), encoding="utf-8")
    fixture = Fixture(tmp_path=tmp_path)
    fixture.verify_existing_bond_conversion_factors_are_updated()


class Fixture:
    def __init__(self, tmp_path: Path):
        self._eurex_dir = tmp_path / "eurex"
        self._eurex_dir.mkdir()
        self._portfolio_file = tmp_path / "portfolio.json"
        (self._eurex_dir / "2026-03-09_deliverable_bonds.csv").write_text(
            _CSV_CONTENT, encoding="utf-8"
        )

    def verify_bonds_are_saved_to_portfolio(self):
        RefreshBondPortfolio(
            eurex_data_dir=self._eurex_dir,
            portfolio_file=self._portfolio_file,
        ).execute()

        assert self._portfolio_file.exists()
        data = json.loads(self._portfolio_file.read_text(encoding="utf-8"))
        assert "DE0001102580" in data
        assert "DE0001104883" in data
        assert data["DE0001102580"]["CouponRate"] == pytest.approx(2.5)
        assert data["DE0001104883"]["CouponRate"] == pytest.approx(2.2)

    def verify_existing_bond_conversion_factors_are_updated(self):
        RefreshBondPortfolio(
            eurex_data_dir=self._eurex_dir,
            portfolio_file=self._portfolio_file,
        ).execute()

        data = json.loads(self._portfolio_file.read_text(encoding="utf-8"))
        cf = data["DE0001102580"]["CF"]
        assert cf.get("FGBLH26") == pytest.approx(0.651234)
        assert cf.get("FGBLM26") == pytest.approx(0.654321)
