import logging
from decimal import Decimal

from tinkoff.invest.utils import quotation_to_decimal

from configuration.settings import StrategySettings
from data_provider.base_data_provider import IDataProvider
from history_tests.trading_emulator.base_trading_emulator import ITradingEmulator
from trade_system.signal import SignalType
from trade_system.strategies.base_strategy import IStrategy
from trade_system.strategies.strategy_factory import StrategyFactory
from history_tests.test_results import TestResults

__all__ = ("MovingStopEmulator")

logger = logging.getLogger(__name__)


class MovingStopEmulator(ITradingEmulator):
    """
    Class encapsulate trading based on moving stop strategy
    """

    def __init__(
            self,
            strategy_name: str,
            strategy_settings: StrategySettings,
            data_provider: IDataProvider,
            skip_reverse_signal: bool,
            update_stop_to_no_loss: bool
    ) -> None:
        self.__strategy: IStrategy = StrategyFactory.new_factory(
            strategy_name,
            strategy_settings
        )
        self.__data_provider = data_provider

        self.__skip_reverse_signal = skip_reverse_signal
        self.__update_stop_to_no_loss = update_stop_to_no_loss

    def emulate_trading(
            self,
            from_days: int
    ) -> TestResults:
        logger.info(f"Start MovingStopEmulator test: {self.__strategy}, "
                    f"figi: {self.__strategy.settings.figi}, from_days: {from_days}")

        test_result = TestResults()
        price_diff = Decimal(0)

        for candle in self.__data_provider.provide(self.__strategy.settings.figi, from_days):
            current_price_level = quotation_to_decimal(candle.close)

            # Check price from candle for stop price level
            if test_result.current_position:
                high = quotation_to_decimal(candle.high)
                low = quotation_to_decimal(candle.low)

                # Logic is:
                # if stop price level is between high and low, then stop will be executed
                # candle.close is the nearest price level to emulate price of closed position
                if low <= test_result.current_position.signal.stop_loss_level <= high:
                    logger.info("Test STOP LOSS executed")
                    logger.info(f"CANDLE: {candle}")
                    logger.info(f"Signal: {test_result.current_position.signal}")

                    test_result.close_position(current_price_level)
                else:
                    # if price level moved on high (long) or low (short) price, then stop price level will be moved also
                    current_price_diff = current_price_level - price_diff
                    logger.info(f"Current price diff with stop {current_price_diff}")

                    # Long
                    if test_result.current_position.signal.signal_type == SignalType.LONG:
                        # if current price goes up then stop level will rise also
                        if current_price_diff > test_result.current_position.signal.stop_loss_level:
                            test_result.current_position.signal.stop_loss_level = current_price_diff
                            logger.info(f"Update stop level (diff) to {test_result.current_position.signal.stop_loss_level}")

                        # update stop level to open position if price higher than open
                        # stop to "NO LOSS" price level
                        if self.__update_stop_to_no_loss \
                                and test_result.current_position.signal.stop_loss_level < test_result.current_position.open_level < current_price_level:
                            test_result.current_position.signal.stop_loss_level = test_result.current_position.open_level
                            logger.info(f"Update stop level (open) to {test_result.current_position.signal.stop_loss_level}")

                    # Short
                    elif test_result.current_position.signal.signal_type == SignalType.SHORT:
                        # if current price goes down then stop level will down also
                        if current_price_diff < test_result.current_position.signal.stop_loss_level:
                            test_result.current_position.signal.stop_loss_level = current_price_diff
                            logger.info(f"Update stop level (diff) to {test_result.current_position.signal.stop_loss_level}")

                        # update stop level to open position if price lower than open
                        # stop to "NO LOSS" price level
                        if self.__update_stop_to_no_loss \
                                and test_result.current_position.signal.stop_loss_level > test_result.current_position.open_level > current_price_level:
                            test_result.current_position.signal.stop_loss_level = test_result.current_position.open_level
                            logger.info(f"Update stop level to (open) {test_result.current_position.signal.stop_loss_level}")

            signal = self.__strategy.analyze_candle(candle)
            if signal:
                logger.info(f"New Signal: {signal}")

                if test_result.current_position:
                    # skip signal if skip setting is on or signals have the same type
                    if self.__skip_reverse_signal \
                            or test_result.current_position.signal.signal_type == signal.signal_type:
                        logger.info("Signal skipped. Old still alive")
                        continue
                    else:
                        # close current position and open a new
                        test_result.close_position(current_price_level)

                # candle.close is the nearest price level to emulate price of open position
                test_result.open_position(signal, current_price_level)

                # save diff from signal to move stop
                price_diff = current_price_level - signal.stop_loss_level
                logger.info(f"New price diff: {price_diff}")

        logger.info(f"Tests were completed")

        return test_result

    def __str__(self):
        """Override method for better representation in test results"""
        return f"{self.__class__.__name__}(skip reverse={self.__skip_reverse_signal}, " \
               f"no loss level={self.__update_stop_to_no_loss})"
