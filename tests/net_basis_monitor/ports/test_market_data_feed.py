from typing import List

from src.net_basis_monitor.adapters.market_data_feed.stub_market_data_feed import StubMarketDataFeed
from src.net_basis_monitor.core.models.value_objects.tick import Tick


def test_market_data_subscription():
    fixture = Fixture()
    feed = fixture.feed
    feed.subscribe(["DE0001135275", "FGBLM6"], ["BID", "ASK"])
    fixture.verify_subscribed(["DE0001135275", "FGBLM6"])


def test_market_data_push_update():
    fixture = Fixture()
    feed = fixture.feed
    feed.start(lambda tick: fixture.received_ticks.append(tick))
    
    tick = Tick(ric="DE0001135275", bid=100.0, ask=100.1)
    feed.push_update(tick)
    fixture.verify_tick_received(tick)
    
    feed.stop()
    fixture.verify_disconnected()
    
    feed.push_update(tick)
    fixture.verify_tick_count(1)


def test_market_data_unsubscribe():
    instruments = ["DE0001135275", "FGBLM6"]
    fixture = Fixture()
    feed = fixture.feed
    feed.subscribe(instruments, ["BID", "ASK"])
    feed.unsubscribe(["DE0001135275"])
    
    fixture.verify_subscribed(["FGBLM6"])
    fixture.verify_not_subscribed(["DE0001135275"])


class Fixture:
    def __init__(self):
        self.feed = StubMarketDataFeed()
        self.received_ticks: List[Tick] = []

    def verify_subscribed(self, expected_instruments: List[str]):
        subscribed = self.feed.get_subscribed_instruments()
        for instrument in expected_instruments:
            assert instrument in subscribed
        assert self.feed.is_connected() is True

    def verify_not_subscribed(self, expected_missing: List[str]):
        subscribed = self.feed.get_subscribed_instruments()
        for instrument in expected_missing:
            assert instrument not in subscribed

    def verify_tick_received(self, expected_tick: Tick):
        assert len(self.received_ticks) > 0
        assert self.received_ticks[-1] == expected_tick

    def verify_tick_count(self, count: int):
        assert len(self.received_ticks) == count

    def verify_disconnected(self):
        assert self.feed.is_connected() is False

