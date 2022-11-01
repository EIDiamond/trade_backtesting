import logging
from typing import Generator

from tinkoff.invest import CandleInterval

from data_provider.base_data_provider import IDataProvider
from data_provider.internal_candle import InternalCandle
from invest_api.services.client_service import ClientService
from invest_api.utils import historic_candle_to_internal

__all__ = ("TinkoffHistoric")


logger = logging.getLogger(__name__)


class TinkoffHistoric(IDataProvider):
    """Data provider from tinkoff historic candles (api download_historic_candle)"""
    def __init__(self, token: str, app_name: str) -> None:
        self.__client_service = ClientService(token, app_name)

    def provide(self, figi: str, from_days: int) -> Generator[InternalCandle, None, None]:
        for candle in self.__client_service.download_historic_candle(
            figi,
            from_days,
            CandleInterval.CANDLE_INTERVAL_1_MIN
        ):
            yield historic_candle_to_internal(candle)
