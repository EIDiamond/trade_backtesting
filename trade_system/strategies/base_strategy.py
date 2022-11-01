import abc
from typing import Optional

from configuration.settings import StrategySettings
from data_provider.internal_candle import InternalCandle
from trade_system.signal import Signal

__all__ = ("IStrategy")


class IStrategy(abc.ABC):
    """Interface for strategy classes """
    @property
    @abc.abstractmethod
    def settings(self) -> StrategySettings:
        pass

    @abc.abstractmethod
    def analyze_candle(self, candle: InternalCandle) -> Optional[Signal]:
        pass
