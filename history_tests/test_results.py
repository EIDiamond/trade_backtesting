from decimal import Decimal
from typing import Optional

from trade_system.signal import Signal

__all__ = ("TestResults", "TestPosition")


class TestPosition:
    def __init__(self, signal: Signal, open_level: Decimal) -> None:
        self.__signal = signal
        self.__open_level = open_level
        self.__close_level = Decimal(0)

    @property
    def signal(self) -> Signal:
        return self.__signal

    @property
    def open_level(self) -> Decimal:
        return self.__open_level

    @property
    def close_level(self) -> Decimal:
        return self.__close_level

    def close_position(self, close_level: Decimal) -> None:
        self.__close_level = close_level


class TestResults:
    """Class keeps information about trading result (emulation):
    - Current open position
    - All positions for history
    - Signal for position
    - Open and close price level
    """

    def __init__(self) -> None:
        self.__current_position: Optional[TestPosition] = None
        self.__executed_orders: list[TestPosition] = []

    @property
    def current_position(self) -> TestPosition:
        return self.__current_position

    @property
    def executed_orders(self) -> list[TestPosition]:
        return self.__executed_orders

    def open_position(self, signal: Signal, open_level: Decimal) -> None:
        if self.__current_position:
            raise Exception("Cannot open position. Current position is exist.")
        else:
            self.__current_position = TestPosition(signal, open_level)

    def close_position(self, close_level: Decimal) -> None:
        if self.__current_position:
            self.__current_position.close_position(close_level)

            self.__executed_orders.append(self.__current_position)
            self.__current_position = None
        else:
            raise Exception("Cannot close position. Current position isn't exist.")
