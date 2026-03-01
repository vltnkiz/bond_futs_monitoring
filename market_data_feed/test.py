import time

from market_data_feed.adapters.market_data_feed.lseg_market_data_feed import LSEGMarketDataFeed
from market_data_feed.core.models.tick import Tick


def on_tick(tick: Tick) -> None:
    snapshot_label = "[SNAPSHOT]" if tick.is_snapshot else "[UPDATE]  "
    print(
        f"{snapshot_label} {tick.timestamp:%H:%M:%S.%f} | "
        f"{tick.ric:<12} | "
        f"bid={tick.bid!s:<10} ask={tick.ask!s:<10} "
        f"bidsize={tick.bidszie!s:<10} asksize={tick.asksize!s:<10}"
    )


if __name__ == "__main__":
    feed = LSEGMarketDataFeed()

    feed.subscribe(
        instruments=["FGBLH26", "FGBLM26"],
        fields=["CF_BID", "CF_ASK", "BIDSIZE", "ASKSIZE"],
    )

    print("Starting market data feed for 60 seconds...")
    feed.start(on_tick=on_tick)

    time.sleep(60)

    print("Stopping feed.")
    feed.stop()