import abc

from history_tests.test_results import TestResults

__all__ = ("ITradingEmulator")


class ITradingEmulator(abc.ABC):
    """Interface to emulate different style of trading"""
    @abc.abstractmethod
    def emulate_trading(self, from_days: int) -> TestResults:
        pass
