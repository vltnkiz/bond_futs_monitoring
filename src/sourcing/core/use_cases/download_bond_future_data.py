from pathlib import Path

from src.sourcing.core.ports import FuturesBasketDownloader


class DownloadBondFutureData:
    def __init__(self, futures_basket_downloader: FuturesBasketDownloader, save_dir: Path):
        self.__futures_basket_downloader = futures_basket_downloader
        self.__save_dir = save_dir

    def execute(self) -> Path:
        return self.__futures_basket_downloader.download(save_dir=self.__save_dir)