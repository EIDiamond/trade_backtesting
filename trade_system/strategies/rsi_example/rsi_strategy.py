import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

import pandas as pd
from tinkoff.invest.utils import quotation_to_decimal

from configuration.settings import StrategySettings
from data_provider.internal_candle import InternalCandle
from trade_system.signal import Signal, SignalType
from trade_system.strategies.base_strategy import IStrategy

__all__ = ("RsiStrategy")

logger = logging.getLogger(__name__)


@dataclass(eq=False, repr=True)
class FloatCandle:
    """Data class for Pandas calculations.
    float type is a mistake and shame. Using it just for example.
    Do not use it in production code.
    """
    open: float
    high: float
    low: float
    close: float
    volume: int
    time: datetime


class RsiStrategy(IStrategy):
    """
    Example of trade strategy based on RSI indicator (self-made).
    Part of example from research project [analyze_market_data](https://github.com/EIDiamond/analyze_market_data)
    IMPORTANT: DO NOT USE IT FOR REAL TRADING!
    """
    # Consts for read and parse dict with strategy configuration

    __LENGTH = "LENGTH"
    __SOURCE = "SOURCE"
    __INTERVAL_MIN = "INTERVAL_MIN"
    __LONG_RSI_LEVEL = "LONG_RSI_LEVEL"
    __SHORT_RSI_LEVEL = "SHORT_RSI_LEVEL"

    __LONG_TAKE_NAME = "LONG_TAKE"
    __LONG_STOP_NAME = "LONG_STOP"
    __SHORT_TAKE_NAME = "SHORT_TAKE"
    __SHORT_STOP_NAME = "SHORT_STOP"

    def __init__(self, settings: StrategySettings) -> None:
        self.__settings = settings

        self.__length = int(settings.settings[self.__LENGTH])
        self.__source = str(settings.settings[self.__SOURCE])
        self.__interval = int(settings.settings[self.__INTERVAL_MIN])
        self.__long_rsi = int(settings.settings[self.__LONG_RSI_LEVEL])
        self.__short_rsi = int(settings.settings[self.__SHORT_RSI_LEVEL])

        self.__long_take = Decimal(settings.settings[self.__LONG_TAKE_NAME])
        self.__long_stop = Decimal(settings.settings[self.__LONG_STOP_NAME])

        self.__short_take = Decimal(settings.settings[self.__SHORT_TAKE_NAME])
        self.__short_stop = Decimal(settings.settings[self.__SHORT_STOP_NAME])

        self.__recent_candles: list[InternalCandle] = []
        self.__current_candle: Optional[InternalCandle] = None

    @property
    def settings(self) -> StrategySettings:
        return self.__settings

    def analyze_candle(self, candle: InternalCandle) -> Optional[Signal]:
        """
        The method analyzes candle and returns a decision.
        """
        logger.debug(f"Start analyze candle for {self.settings.figi} strategy {__name__}. {candle} ")

        result: Optional[Signal] = None

        if self.__current_candle:
            if candle.time < self.__current_candle.time:
                # it happens sometimes (based on API documentation). Just cover this situation.
                logger.debug("Skip candle from past.")
                return None

            if candle.time > self.__current_candle.time:
                if self.__update_recent_candles(self.__current_candle):

                    if self.__is_match_long():
                        logger.info(f"Signal (LONG) {self.settings.figi} has been found.")
                        result = self.__make_signal(SignalType.LONG, self.__long_take, self.__long_stop)

                    elif self.settings.short_enabled_flag and self.__is_match_short():
                        logger.info(f"Signal (SHORT) {self.settings.figi} has been found.")
                        result = self.__make_signal(SignalType.SHORT, self.__short_take, self.__short_stop)

        self.__current_candle = candle

        return result

    def __update_recent_candles(self, candle: InternalCandle) -> bool:
        # update 1 minute candle to candle with self.__interval minutes interval
        if len(self.__recent_candles) > 0:
            current_candle = self.__recent_candles[len(self.__recent_candles) - 1]
            # calculate difference between first candle in interval and new candle
            diff_sec = (candle.time - current_candle.time).seconds
            if diff_sec >= (self.__interval * 60):
                # just add a new candle.
                self.__recent_candles.append(candle)
            else:
                # interval still going, so update current candle with the latest information
                current_candle.close = candle.close
                current_candle.volume += candle.volume
                current_candle.high = candle.high \
                    if (quotation_to_decimal(current_candle.high) < quotation_to_decimal(candle.high)) \
                    else current_candle.high
                current_candle.low = candle.low \
                    if (quotation_to_decimal(current_candle.low) > quotation_to_decimal(candle.low)) \
                    else current_candle.low
        else:
            # just add a new candle to empty cache
            self.__recent_candles.append(candle)

        if len(self.__recent_candles) < (self.__length + 1):
            logger.debug(f"Candles in cache are low than required")
            return False

        sorted(self.__recent_candles, key=lambda x: x.time)

        # keep only self.__length candles in cache
        if len(self.__recent_candles) > (self.__length + 1):
            self.__recent_candles = self.__recent_candles[len(self.__recent_candles) - self.__length - 1:]

        return True

    def __is_match_long(self) -> bool:
        """
        Check for LONG signal. All candles in cache:
        Make a Signal if rsi < 25
        """

        return self.__current_rsi() < self.__long_rsi

    def __is_match_short(self) -> bool:
        """
        Check for SHORT signal. All candles in cache:
        Make a Signal if rsi > 75
        """

        return self.__current_rsi() > self.__short_rsi

    def __make_signal(
            self,
            signal_type: SignalType,
            profit_multy: Decimal,
            stop_multy: Decimal
    ) -> Signal:
        # take and stop based on configuration by close price level (close for last price)
        last_candle = self.__recent_candles[len(self.__recent_candles) - 1]

        signal = Signal(
            figi=self.settings.figi,
            signal_type=signal_type,
            take_profit_level=quotation_to_decimal(last_candle.close) * profit_multy,
            stop_loss_level=quotation_to_decimal(last_candle.close) * stop_multy
        )

        logger.info(f"Make Signal: {signal}")

        return signal

    def __convert_candles(self) -> list[FloatCandle]:
        logger.info(f"Fill candles")
        candles: list[FloatCandle] = []

        for candle in self.__recent_candles:
            candles.append(
                FloatCandle(
                    open=float(quotation_to_decimal(candle.open)),
                    high=float(quotation_to_decimal(candle.high)),
                    low=float(quotation_to_decimal(candle.low)),
                    close=float(quotation_to_decimal(candle.close)),
                    volume=candle.volume,
                    time=candle.time
                )
            )

        return candles

    def __calculate_rsi(
            self,
            candles: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Wells Wilder's RSI calculation developed via the Pandas library.
        Based on: https://github.com/alphazwest
        """

        # Calculate Price Differences using the column specified as price (self.__source).
        candles['diff'] = candles[self.__source].diff(1)

        # Calculate Avg. Gains/Losses
        candles['gain'] = candles['diff'].clip(lower=0)
        candles['loss'] = candles['diff'].clip(upper=0).abs()

        # Get initial Averages
        candles['avg_gain'] = candles['gain'].rolling(window=self.__length, min_periods=self.__length).mean()[:self.__length + 1]
        candles['avg_loss'] = candles['loss'].rolling(window=self.__length, min_periods=self.__length).mean()[:self.__length + 1]
        candles['avg_loss_no_slice'] = candles['loss'].rolling(window=self.__length, min_periods=self.__length).mean()

        # Calculate Average Gains
        for i, row in enumerate(candles['avg_gain'].iloc[self.__length + 1:]):
            candles['avg_gain'].iloc[i + self.__length + 1] = \
                (candles['avg_gain'].iloc[i + self.__length] *
                 (self.__length - 1) +
                 candles['gain'].iloc[i + self.__length + 1]) \
                / self.__length

        # Calculate Average Losses
        for i, row in enumerate(candles['avg_loss'].iloc[self.__length + 1:]):
            candles['avg_loss'].iloc[i + self.__length + 1] = \
                (candles['avg_loss'].iloc[i + self.__length] *
                 (self.__length - 1) +
                 candles['loss'].iloc[i + self.__length + 1]) \
                / self.__length

        # Calculate RS Values
        candles['rs'] = candles['avg_gain'] / candles['avg_loss']

        # Calculate RSI
        candles['rsi'] = 100 - (100 / (1.0 + candles['rs']))

        return candles

    def __current_rsi(self) -> float:
        logger.info(f"Start RSI calculation")

        candles_rsi = self.__calculate_rsi(pd.DataFrame(self.__convert_candles()))
        current_rsi = candles_rsi.iat[len(candles_rsi) - 1, len(candles_rsi.columns) - 1]

        logger.info(f"RSI calculation. Current is {current_rsi}")

        return current_rsi
