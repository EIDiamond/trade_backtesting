import logging

from tinkoff.invest.utils import quotation_to_decimal

from configuration.settings import StrategySettings
from data_provider.base_data_provider import IDataProvider
from history_tests.trading_emulator.base_trading_emulator import ITradingEmulator
from trade_system.signal import SignalType
from trade_system.strategies.base_strategy import IStrategy
from trade_system.strategies.strategy_factory import StrategyFactory
from history_tests.test_results import TestResults

logger = logging.getLogger(__name__)


class AllFromStrategyEmulator(ITradingEmulator):
    """
    Class encapsulate trading based on stop and take signals from strategy only
    """

    def __init__(
            self,
            strategy_name: str,
            strategy_settings: StrategySettings,
            data_provider: IDataProvider
    ) -> None:
        self.__strategy: IStrategy = StrategyFactory.new_factory(
            strategy_name,
            strategy_settings
        )
        self.__data_provider = data_provider

    def emulate_trading(
            self,
            from_days: int
    ) -> TestResults:
        logger.info(
            f"Start AllFromStrategyEmulator test: {self.__strategy}, figi: {self.__strategy.settings.figi}, "
            f"from_days: {from_days}")

        test_result = TestResults()

        for candle in self.__data_provider.provide(self.__strategy.settings.figi, from_days):
            signal = self.__strategy.analyze_candle(candle)

            if signal:
                logger.info(f"New Signal: {signal}")

                if test_result.current_position:
                    # if position has been already opened
                    if test_result.current_position.signal.signal_type == signal.signal_type:
                        # skip signal if new and current have the same type
                        logger.info("Signal skipped. Old still alive")
                    elif signal.signal_type == SignalType.CLOSE:
                        # close position if signal to Close position
                        logger.info("Signal CLOSE. Close position")
                        test_result.close_position(quotation_to_decimal(candle.close))
                    else:
                        # close current position and open a new
                        logger.info("Close current position and open a new")
                        test_result.close_position(quotation_to_decimal(candle.close))
                        test_result.open_position(signal, quotation_to_decimal(candle.close))
                else:
                    # no current position - open a new position
                    logger.info("Open a new position")
                    test_result.open_position(signal, quotation_to_decimal(candle.close))

        logger.info(f"Tests were completed")

        return test_result

    def __str__(self):
        """Override method for better representation in test results"""
        return f"{self.__class__.__name__}"
