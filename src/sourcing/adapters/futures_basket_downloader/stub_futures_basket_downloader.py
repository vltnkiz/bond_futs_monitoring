
from pathlib import Path

from src.sourcing.core.ports import FuturesBasketDownloader

_STUB_CSV_CONTENT = """#Contract;ISIN;Coupon;Maturity;ConvFac
FGBL 2026-03-06;DE0001102580;2.5;15.08.2046;0.651234
FGBL 2026-06-08;DE0001102580;2.5;15.08.2046;0.654321
FGBM 2026-03-06;DE0001104883;2.2;15.02.2031;0.881100
FGBM 2026-06-08;DE0001104883;2.2;15.02.2031;0.884500
"""


class StubFuturesBasketDownloader(FuturesBasketDownloader):

    _STUB_FILENAME = "stub_deliverable_bonds.csv"

    def download(self, save_dir: Path) -> Path:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        path = save_dir / self._STUB_FILENAME
        path.write_text(_STUB_CSV_CONTENT, encoding="utf-8")
        return path
