import json
from pathlib import Path

import pytest

from src.sourcing.core.use_cases.refresh_future_portfolio import RefreshFuturePortfolio

_CSV_CONTENT = """\
#Contract;ISIN;Coupon;Maturity;ConvFac
FGBL 2026-03-06;DE0001102580;2.5;15.08.2046;0.651234
FGBL 2026-03-06;DE000BU3Z047;1.8;15.08.2053;0.523100
FGBL 2026-06-08;DE0001102580;2.5;15.08.2046;0.654321
FGBM 2026-03-06;DE0001104883;2.2;15.02.2031;0.881100
"""


def test_futures_are_saved_to_portfolio(tmp_path):
    eurex_dir = tmp_path / "eurex"
    portfolio_file = tmp_path / "future_definition.json"
    fixture = Fixture(
        eurex_dir=eurex_dir,
        portfolio_file=portfolio_file,
    )
    fixture.verify_futures_are_saved_to_portfolio()


def test_existing_future_deliverable_bonds_are_updated(tmp_path):
    old_portfolio = {
        "FGBLH26": {
            "ContractSymbol": "FGBLH26",
            "ExpiryMonth": "Mar-2026",
            "LastTradingDate": "2026-03-06 00:00:00",
            "DeliveryDate": "2026-03-10",
            "NotionalValue": 100000.0,
            "TickValue": 10.0,
            "NotionalCoupon": 6.0,
            "DeliverableBonds": ["DE000OLD00001"],
        }
    }
    eurex_dir = tmp_path / "eurex"
    portfolio_file = tmp_path / "future_definition.json"    
    portfolio_file.write_text(json.dumps(old_portfolio), encoding="utf-8")
    fixture = Fixture(
        eurex_dir=eurex_dir,
        portfolio_file=portfolio_file,
    )
    
    fixture.verify_existing_future_deliverable_bonds_are_updated()


class Fixture:
    def __init__(self, eurex_dir: Path, portfolio_file: Path):
        self._eurex_dir = eurex_dir
        self._portfolio_file = portfolio_file
        eurex_dir.mkdir(exist_ok=True)
        (eurex_dir / "2026-03-09_deliverable_bonds.csv").write_text(
            _CSV_CONTENT, encoding="utf-8"
        )

    def verify_futures_are_saved_to_portfolio(self):
        RefreshFuturePortfolio(eurex_data_dir=self._eurex_dir, portfolio_file=self._portfolio_file).execute()

        assert self._portfolio_file.exists()
        data = json.loads(self._portfolio_file.read_text(encoding="utf-8"))
        assert "FGBLH26" in data
        assert "FGBLM26" in data
        assert "FGBMH26" in data
        assert set(data["FGBLH26"]["DeliverableBonds"]) == {"DE0001102580", "DE000BU3Z047"}
        assert set(data["FGBLM26"]["DeliverableBonds"]) == {"DE0001102580"}

    def verify_existing_future_deliverable_bonds_are_updated(self):
        RefreshFuturePortfolio(eurex_data_dir=self._eurex_dir, portfolio_file=self._portfolio_file).execute()

        data = json.loads(self._portfolio_file.read_text(encoding="utf-8"))
        bonds = set(data["FGBLH26"]["DeliverableBonds"])
        assert "DE000OLD00001" not in bonds
        assert "DE0001102580" in bonds
        assert "DE000BU3Z047" in bonds
        assert data["FGBLH26"]["NotionalValue"] == pytest.approx(100000.0)
        assert data["FGBLH26"]["TickValue"] == pytest.approx(10.0)
