import csv
from pathlib import Path
from typing import Dict, List

from src.shared.utils.convert_contract_to_symbol import convert_contract_symbol
from src.sourcing.core.models.future import Future
from src.sourcing.core.models.future_definition import FuturePortfolio


class RefreshFuturePortfolio:
    def __init__(self, eurex_data_dir: Path, portfolio_file: Path):
        self.__eurex_data_dir = eurex_data_dir
        self.__portfolio_file = portfolio_file

    def execute(self) -> None:
        csv_path = self._find_latest_csv()
        futures_from_csv = self._parse_csv(csv_path)
        portfolio = FuturePortfolio(str(self.__portfolio_file))
        self._merge(portfolio, futures_from_csv)
        portfolio.save()

    def _find_latest_csv(self) -> Path:
        csv_files = sorted(self.__eurex_data_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {self.__eurex_data_dir}")
        return csv_files[-1]

    def _parse_csv(self, csv_path: Path) -> List[Future]:
        futures_by_symbol: Dict[str, Future] = {}

        with open(csv_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh, delimiter=";")
            for row in reader:
                contract_symbol = convert_contract_symbol(row["#Contract"].strip())
                isin = row["ISIN"].strip()

                if contract_symbol not in futures_by_symbol:
                    futures_by_symbol[contract_symbol] = Future(
                        ContractSymbol=contract_symbol,
                        ExpiryMonth="",
                        LastTradingDate="",
                        DeliveryDate="",
                        NotionalValue=0.0,
                        TickValue=0.0,
                        NotionalCoupon=6.0,
                    )

                futures_by_symbol[contract_symbol].add_deliverable_bond(isin)

        return list(futures_by_symbol.values())

    def _merge(self, portfolio: FuturePortfolio, futures: List[Future]) -> None:
        for future in futures:
            existing = portfolio.get_future(future.contract_symbol)
            if existing is not None:
                existing.replace_deliverable_bonds(future.get_all_deliverable_bonds())
            else:
                portfolio.add_future(future)
