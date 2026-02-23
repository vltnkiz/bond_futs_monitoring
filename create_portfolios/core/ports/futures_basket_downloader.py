from abc import ABC, abstractmethod
from typing import Optional


class BasketDownloader(ABC):
    @abstractmethod
    def download(self, save_dir: str = "./eurex_files") -> Optional[str]:
        pass
