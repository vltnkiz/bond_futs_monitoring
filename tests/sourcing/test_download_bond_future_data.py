
from pathlib import Path

from src.sourcing.adapters.futures_basket_downloader.stub_futures_basket_downloader import StubFuturesBasketDownloader
from src.sourcing.core.ports import FuturesBasketDownloader
from src.sourcing.core.use_cases.download_bond_future_data import DownloadBondFutureData


def test_download_bond_future_data(tmp_path):
    save_dir = tmp_path / "eurex"
    fixture = Fixture(
        futures_basket_downloader=StubFuturesBasketDownloader(),
        save_dir=save_dir,
    )
    fixture.verify_download_bond_future_data()


class Fixture:
    def __init__(self, futures_basket_downloader: FuturesBasketDownloader, save_dir: Path):
        self._futures_basket_downloader = futures_basket_downloader
        self._save_dir = save_dir

    def verify_download_bond_future_data(self):
        csv_path = DownloadBondFutureData(
            futures_basket_downloader=self._futures_basket_downloader,
            save_dir=self._save_dir,
        ).execute()

        assert csv_path is not None
        assert csv_path.exists()
        assert csv_path.parent == self._save_dir
