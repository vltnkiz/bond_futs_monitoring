from abc import ABC, abstractmethod
from pathlib import Path


class FuturesBasketDownloader(ABC):
    @abstractmethod
    def download(self, save_dir: str) -> Path:
        pass
