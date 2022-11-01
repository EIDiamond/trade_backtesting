import logging
from typing import Generator

from data_provider.base_data_provider import IDataProvider
from data_provider.internal_candle import InternalCandle
from data_provider.tinkoff_downloaded.csv_data_storage import CSVDataStorageReader

__all__ = ("TinkoffDownloaded")

logger = logging.getLogger(__name__)


class TinkoffDownloaded(IDataProvider):
    """Data provider for downloaded market data by (data_collectors\tinkoff_stream_py) project"""
    def __init__(self, root_path: str) -> None:
        self.__data_reader = CSVDataStorageReader(root_path)

    def provide(self, figi: str, from_days: int) -> Generator[InternalCandle, None, None]:
        for candle in self.__data_reader.read_candles(figi, from_days):
            yield InternalCandle(
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                time=candle.time
            )
