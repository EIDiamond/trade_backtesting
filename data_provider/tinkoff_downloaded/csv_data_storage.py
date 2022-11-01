import csv
from datetime import datetime, timezone, timedelta
import logging
from decimal import Decimal
from pathlib import Path
from typing import Generator

from tinkoff.invest import Candle, Trade, LastPrice, TradeDirection
from tinkoff.invest.utils import decimal_to_quotation

__all__ = ("CSVDataStorageReader")

logger = logging.getLogger(__name__)


class CSVDataStorageReader:
    __FILE_NAME = "market_data.csv"

    __CANDLE_TYPE_FOLDER = "candle"
    __TRADE_TYPE_FOLDER = "trade"
    __LAST_PRICE_TYPE_FOLDER = "last_price"

    def __init__(self, root_path: str) -> None:
        self.__root_path = root_path

        if not self.__root_path:
            logger.error(f"Storage reader init failed: root path is empty!")

            raise Exception(f"CSVDataStorageReader: root path is empty!")

    def read_candles(self, figi: str, from_days: int) -> Generator[Candle, None, None]:
        """
        Headers in candle csv file:
        open, close, high, low, volume, time
        """

        logger.info(f"Start read candles from root folder:{self.__root_path}, figi:{figi}, from_days:{from_days}")

        try:
            for row in self.__read_market_files(
                    figi,
                    self.__CANDLE_TYPE_FOLDER,
                    from_days
            ):
                yield Candle(
                    figi=figi,
                    open=decimal_to_quotation(Decimal(row[0])),
                    high=decimal_to_quotation(Decimal(row[2])),
                    low=decimal_to_quotation(Decimal(row[3])),
                    close=decimal_to_quotation(Decimal(row[1])),
                    volume=int(row[4]),
                    time=datetime.strptime(row[5], '%Y-%m-%d %H:%M:%S%z')  # 2022-09-02 07:34:00+00:00
                )
        except Exception as ex:
            logger.error(f"Error while read candle data from files: {repr(ex)}")

    def read_trade(self, figi: str, from_days: int) -> Generator[Trade, None, None]:
        """
        Headers in trade csv file:
        direction, price, quantity, time
        """

        logger.info(f"Start read trades from root folder:{self.__root_path}, figi:{figi}, from_days:{from_days}")

        try:
            for row in self.__read_market_files(
                    figi,
                    self.__TRADE_TYPE_FOLDER,
                    from_days
            ):
                yield Trade(
                    figi=figi,
                    direction=TradeDirection(int(row[0])),
                    price=decimal_to_quotation(Decimal(row[1])),
                    quantity=int(row[2]),
                    time=datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S%z')  # 2022-09-02 07:34:00+00:00
                )
        except Exception as ex:
            logger.error(f"Error while read trade data from files: {repr(ex)}")

    def read_last_price(self, figi: str, from_days: int) -> Generator[LastPrice, None, None]:
        """
        Headers in last_price csv file:
        price, time
        """

        logger.info(f"Start read last prices from root folder:{self.__root_path}, figi:{figi}, from_days:{from_days}")

        try:
            for row in self.__read_market_files(
                    figi,
                    self.__LAST_PRICE_TYPE_FOLDER,
                    from_days
            ):
                yield LastPrice(
                    figi=figi,
                    price=decimal_to_quotation(Decimal(row[0])),
                    time=datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S%z')  # 2022-09-02 07:34:00+00:00
                )
        except Exception as ex:
            logger.error(f"Error while read last price data from files: {repr(ex)}")

    def __read_market_files(self, figi: str, type_folder: str, from_days: int) -> Generator[str, None, None]:
        for data_file_path in self.__get_market_data_file_paths(
                figi,
                type_folder,
                from_days
        ):
            try:
                for row in CSVDataStorageReader.__read_data_file(data_file_path):
                    yield row
            except Exception as ex:
                logger.error(f"Error while read data from file {data_file_path}. "
                             f"File has been skipped: {repr(ex)}")

    def __get_market_data_file_paths(self, figi: str, type_folder: str, from_days: int) -> Generator[str, None, None]:
        """
        Folder Structure is:
        root_path
            figi
                type_folder
                    year
                        month
                            day
                                {__FILE_NAME}
        """

        # check root_path
        root_dir = Path(self.__root_path, figi, type_folder)

        if root_dir.exists():
            from_ = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=from_days) \
                if from_days > 0 else datetime.min

            for year_dir in sorted(root_dir.iterdir(), key=lambda x: int(str(x.name))):
                if from_.year > int(str(year_dir.name)):
                    continue

                for month_dir in sorted(year_dir.iterdir(), key=lambda x: int(str(x.name))):
                    if from_.year == int(str(year_dir.name)) and from_.month > int(str(month_dir.name)):
                        continue

                    for day_dir in sorted(month_dir.iterdir(), key=lambda x: int(str(x.name))):
                        if from_.year == int(str(year_dir.name)) and \
                                from_.month == int(str(month_dir.name)) and from_.day > int(str(day_dir.name)):
                            continue

                        yield str(Path(day_dir, self.__FILE_NAME))
        else:
            logger.info(f"Root directory doesn't exist: {root_dir}.")

    @staticmethod
    def __read_data_file(file_name: str) -> Generator[list[str], None, None]:
        logger.debug(f"Read file: {file_name}")

        with open(file_name, encoding='UTF8', newline="") as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                logger.debug(f"Read row: {row}")

                yield row
