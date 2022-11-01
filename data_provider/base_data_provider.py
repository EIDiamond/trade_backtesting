import abc
from typing import Generator

from tinkoff.invest import HistoricCandle

__all__ = ("IDataProvider")


class IDataProvider(abc.ABC):
    """Interface for different data providers: files, db, api etc."""
    @abc.abstractmethod
    def provide(self, figi: str, from_days: int) -> Generator[HistoricCandle, None, None]:
        pass
