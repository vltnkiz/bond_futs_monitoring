from datetime import date, timedelta

from src.sourcing.core.models.future_definition import FuturePortfolio
from src.sourcing.core.ports import MarketDataProvider

_MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


def _add_business_days(d: date, n: int) -> date:
    current = d
    added = 0
    while added < n:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday–Friday
            added += 1
    return current


class EnrichFutureExpiryDates:
    def __init__(self, future_portfolio: FuturePortfolio, market_data_provider: MarketDataProvider):
        self.__future_portfolio = future_portfolio
        self.__market_data_provider = market_data_provider

    def execute(self) -> None:
        for future in self.__future_portfolio.get_all_futures():
            expiry_date_str = self.__market_data_provider.get(future.contract_symbol, "ExpiryDate")

            if not expiry_date_str or str(expiry_date_str) in ("nan", "None", ""):
                continue

            expiry_date = date.fromisoformat(str(expiry_date_str)[:10])
            expiry_month = f"{_MONTH_NAMES[expiry_date.month]}-{expiry_date.year}"
            last_trading_date = expiry_date.isoformat()
            delivery_date = _add_business_days(expiry_date, 2).isoformat()

            future.enrich_expiry_dates(
                expiry_month=expiry_month,
                last_trading_date=last_trading_date,
                delivery_date=delivery_date,
            )

        self.__future_portfolio.save()
