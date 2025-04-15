from configparser import ConfigParser
from decimal import Decimal
from typing import ValuesView

from configuration.settings import StrategySettings, CommissionSettings

__all__ = ("ProgramConfiguration")


class ProgramConfiguration:
    """
    Represent program configuration
    """
    def __init__(self, file_name: str) -> None:
        # classic ini file
        config = ConfigParser()
        config.read(file_name)

        self.__commission_settings = CommissionSettings(
            every_order=Decimal(config["COMMISSION"]["EVERY_ORDER_PERCENT"])
        )

        self.__test_strategy_settings = \
            StrategySettings(
                name=config["TEST_STRATEGY"]["STRATEGY_NAME"],
                figi=config["TEST_STRATEGY"]["FIGI"],
                ticker=config["TEST_STRATEGY"]["TICKER"],
                settings=config["TEST_STRATEGY_SETTINGS"]
            )

        self.__data_provider_name = config["DATA_PROVIDER"]["NAME"]
        self.__data_provider_from_days = int(config["DATA_PROVIDER"]["FROM_DAYS"])

        self.__data_provider_settings = config["DATA_PROVIDER_SETTINGS"].values()

    @property
    def test_strategy_settings(self) -> StrategySettings:
        return self.__test_strategy_settings

    @property
    def commission_settings(self) -> CommissionSettings:
        return self.__commission_settings

    @property
    def data_provider_name(self) -> str:
        return self.__data_provider_name

    @property
    def data_provider_from_days(self) -> int:
        return self.__data_provider_from_days

    @property
    def data_provider_settings(self) -> ValuesView[str]:
        return self.__data_provider_settings
