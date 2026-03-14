import logging
from pathlib import Path

from src.sourcing.adapters.futures_basket_downloader.eurex_futures_basket_downloader import EurexFuturesBasketDownloader
from src.sourcing.adapters.static_market_data_provider.lseg_static_market_data_provider import LSEGStaticMarketDataProvider
from src.sourcing.core.models.bond_definition import BondPortfolio
from src.sourcing.core.models.future_definition import FuturePortfolio
from src.sourcing.core.use_cases.enrich_bond_coupon_dates import EnrichBondCouponDates
from src.sourcing.core.use_cases.enrich_future_expiry_dates import EnrichFutureExpiryDates
from src.sourcing.core.use_cases.refresh_bond_portfolio import RefreshBondPortfolio
from src.sourcing.core.use_cases.refresh_future_portfolio import RefreshFuturePortfolio

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_logger = logging.getLogger(__name__)

_EUREX_DATA_DIR = Path("data/eurex")
_BOND_PORTFOLIO_FILE = Path("data/portfolios/bond_portfolio.json")
_FUTURE_PORTFOLIO_FILE = Path("data/portfolios/future_definition.json")


def run() -> None:
    eurex_downloader = EurexFuturesBasketDownloader()

    _logger.info("Step 1: Download latest Eurex deliverable bonds CSV")
    csv_path = eurex_downloader.download(save_dir=_EUREX_DATA_DIR)
    _logger.info("Downloaded: %s", csv_path)

    _logger.info("Step 2: Refresh bond portfolio")
    RefreshBondPortfolio(
        eurex_data_dir=_EUREX_DATA_DIR,
        portfolio_file=_BOND_PORTFOLIO_FILE,
    ).execute()

    _logger.info("Step 3: Refresh future portfolio")
    RefreshFuturePortfolio(
        eurex_data_dir=_EUREX_DATA_DIR,
        portfolio_file=_FUTURE_PORTFOLIO_FILE,
    ).execute()

    with LSEGStaticMarketDataProvider() as market_data_provider:
        _logger.info("Step 4: Enrich bond coupon dates")
        EnrichBondCouponDates(
            bond_portfolio=BondPortfolio(str(_BOND_PORTFOLIO_FILE)),
            market_data_provider=market_data_provider,
        ).execute()

        _logger.info("Step 5: Enrich future expiry dates")
        EnrichFutureExpiryDates(
            future_portfolio=FuturePortfolio(str(_FUTURE_PORTFOLIO_FILE)),
            market_data_provider=market_data_provider,
        ).execute()

if __name__ == "__main__":
    run()
