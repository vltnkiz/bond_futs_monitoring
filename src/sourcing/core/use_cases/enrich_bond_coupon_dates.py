import logging
from datetime import date
from dateutil.relativedelta import relativedelta

from src.sourcing.core.models.bond_definition import BondPortfolio
from src.sourcing.core.ports import MarketDataProvider

_logger = logging.getLogger(__name__)


def _ric_from_isin(isin: str) -> str:
    if isin.startswith("FR"):
        return isin
    return f"{isin[0:2]}{isin[5:11]}="


def _coupon_frequency_months(isin: str) -> int:
    if isin.startswith("IT"):
        return 6
    return 12


class EnrichBondCouponDates:
    def __init__(self, bond_portfolio: BondPortfolio, market_data_provider: MarketDataProvider):
        self.__bond_portfolio = bond_portfolio
        self.__market_data_provider = market_data_provider

    def execute(self) -> None:
        for bond in self.__bond_portfolio.get_all_bonds():
            ric = _ric_from_isin(bond.isin)
            raw = self.__market_data_provider.get(ric, "COUPN_DATE")

            if raw is None or str(raw) in ("nan", "None", ""):
                _logger.warning("No COUPN_DATE for %s (RIC: %s) — got: %r", bond.isin, ric, raw)
                continue

            if isinstance(raw, date):
                next_cpn = raw
            else:
                next_cpn = date.fromisoformat(str(raw)[:10])

            freq_months = _coupon_frequency_months(bond.isin)
            last_cpn = next_cpn - relativedelta(months=freq_months)

            bond.enrich_coupon_dates(
                next_coupon_date=next_cpn.isoformat(),
                last_coupon_date=last_cpn.isoformat(),
            )
            _logger.info("Enriched %s: last=%s, next=%s", bond.isin, last_cpn.isoformat(), next_cpn.isoformat())

        self.__bond_portfolio.save()
        self.__market_data_provider.close()
