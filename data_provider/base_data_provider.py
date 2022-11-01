import abc
from typing import Generator

from data_provider.internal_candle import InternalCandle

__all__ = ("IDataProvider")


class IDataProvider(abc.ABC):
    """Interface for different data providers: files, db, api etc."""
    @abc.abstractmethod
    def provide(self, figi: str, from_days: int) -> Generator[InternalCandle, None, None]:
        pass
