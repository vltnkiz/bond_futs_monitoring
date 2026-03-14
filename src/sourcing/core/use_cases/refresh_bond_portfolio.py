import csv
from pathlib import Path
from typing import Dict, List

from src.shared.utils.convert_contract_to_symbol import convert_contract_symbol
from src.sourcing.core.models.bond import Bond
from src.sourcing.core.models.bond_definition import BondPortfolio


class RefreshBondPortfolio:
    _DEFAULT_DAY_COUNT_CONV = "ACT/ACT"

    def __init__(self, eurex_data_dir: Path, portfolio_file: Path):
        self.__eurex_data_dir = eurex_data_dir
        self.__portfolio_file = portfolio_file

    def execute(self) -> None:
        csv_path = self._find_latest_csv()
        bonds_from_csv = self._parse_csv(csv_path)
        portfolio = BondPortfolio(str(self.__portfolio_file))
        self._merge(portfolio, bonds_from_csv)
        portfolio.save()

    def _find_latest_csv(self) -> Path:
        csv_files = sorted(self.__eurex_data_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {self.__eurex_data_dir}")
        return csv_files[-1]

    def _parse_csv(self, csv_path: Path) -> List[Bond]:
        bonds_by_isin: Dict[str, Bond] = {}

        with open(csv_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh, delimiter=";")
            for row in reader:
                isin = row["ISIN"].strip()
                coupon = float(row["Coupon"])
                maturity = row["Maturity"].strip()
                conv_fac = float(row["ConvFac"])
                contract_symbol = convert_contract_symbol(row["#Contract"].strip())

                if isin not in bonds_by_isin:
                    bonds_by_isin[isin] = Bond(
                        ISIN=isin,
                        CouponRate=coupon,
                        MaturityDate=maturity,
                        DayCountConv=self._DEFAULT_DAY_COUNT_CONV,
                    )

                bonds_by_isin[isin].add_conversion_factor(contract_symbol, conv_fac)

        return list(bonds_by_isin.values())

    def _merge(self, portfolio: BondPortfolio, bonds: List[Bond]) -> None:
        for bond in bonds:
            existing = portfolio.get_bond(bond.isin)
            if existing is not None:
                existing.replace_conversion_factors(bond.get_all_conversion_factors())
            else:
                portfolio.add_bond(bond)
