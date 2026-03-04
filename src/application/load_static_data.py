
from pathlib import Path

import pandas as pd

from src.adapters.driven.eurex_futures_basket_downloader import (
    EurexFuturesBasketDownloader,
)
from src.adapters.driven.lseg_market_data_provider import LSEGMarketDataProvider
from src.application.update_bond_definition import update_bond_definition
from src.application.update_future_definition import update_future_definition


def load_all_static_data():
    project_root = Path(__file__).parent.parent.parent
    save_dir = project_root / "data" / "eurex"
    downloader = EurexFuturesBasketDownloader()
    futures_basket_file = downloader.download(save_dir=save_dir)

    df = pd.read_csv(futures_basket_file, sep=";")

    bond_json_file = str(project_root / "data" / "portfolios" / "bond_definition.json")
    future_json_file = str(project_root / "data" / "portfolios" / "future_definition.json")

    update_bond_definition(df, bond_json_file)
    
    market_data_provider = LSEGMarketDataProvider()
    update_future_definition(df, future_json_file, market_data_provider)

if __name__ == "__main__":
    load_all_static_data()