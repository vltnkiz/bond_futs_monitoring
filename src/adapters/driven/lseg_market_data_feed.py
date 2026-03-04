import os
import datetime
import lseg.data as ld
from lseg.data.content import pricing

from src.core.models.tick import Tick
from src.core.ports.driven.market_data_feed import MarketDataFeed, TickHandler
from typing import Any, Optional

class LSEGMarketDataFeed(MarketDataFeed):
    __session: Optional[ld.Session] = None
    __stream: Optional[Any] = None
    
    def __init__(self, config_path: str = None):
        super().__init__()
        self.__instruments_subscribed: set[str] = set()
        self.__fields_subscribed: set[str] = set()
        if config_path:
            os.environ["LD_LIB_CONFIG_PATH"] = config_path
        elif "LD_LIB_CONFIG_PATH" not in os.environ:
            # Try to find config in current directory
            default_path = os.path.join(os.path.dirname(__file__), "lseg-data.config.json")
            if os.path.exists(default_path):
                os.environ["LD_LIB_CONFIG_PATH"] = default_path
        
        # Initialize LSEG session
        ld.open_session()
        self.__session = ld

    def subscribe(self, instruments: list[str], fields: list[str]) -> None:
        self.__instruments_subscribed.update(instruments)
        self.__fields_subscribed.update(fields)
    
    def unsubscribe(self, instruments: list[str]) -> None:
        self.__instruments_subscribed.difference_update(instruments)
    
    def add_instruments(self, instruments: list[str]) -> None:
        self.__instruments_subscribed.update(instruments)
    
    def start(self, on_tick: TickHandler) -> None:
        def _to_tick(fields: dict, ric: str, is_snapshot: bool) -> Tick:
            return Tick(
                ric=ric,
                mid=fields.get("CF_MID"),
                bid=fields.get("CF_BID"),
                ask=fields.get("CF_ASK"),
                bidszie=fields.get("BIDSIZE"),
                asksize=fields.get("ASKSIZE"),
                timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
                is_snapshot=is_snapshot,
                raw=fields,
            )

        self.__stream = pricing.Definition(
            universe=list(self.__instruments_subscribed),
            fields=list(self.__fields_subscribed),
        ).get_stream()

        self.__stream.on_update(lambda fields, instrument, stream: on_tick(_to_tick(fields, instrument, is_snapshot=False)))
        self.__stream.on_refresh(lambda fields, instrument, stream: on_tick(_to_tick(fields, instrument, is_snapshot=True)))
        self.__stream.open(with_updates=True)
    
    def stop(self) -> None:
        if self.__stream:
            self.__stream.close()
        if self.__session:
            self.__session.close_session()
    
    def is_connected(self) -> bool:
        return self.__session is not None and self.__stream is not None and self.__stream.is_open()
    
    @property
    def provider_name(self) -> str:
        return "LSEG"