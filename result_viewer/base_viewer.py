import abc

from history_tests.test_results import TestResults

__all__ = ("IResultViewer")


class IResultViewer(abc.ABC):
    """Interface for different view of trading"""
    @abc.abstractmethod
    def view(self, test_results: dict[str, TestResults]) -> None:
        pass
