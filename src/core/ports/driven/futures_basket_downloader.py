from abc import ABC, abstractmethod
from typing import Optional


class FuturesBasketDownloader(ABC):
    @abstractmethod
    def download(self, save_dir: str) -> Optional[str]:
        pass
