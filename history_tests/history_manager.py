import logging

from history_tests.trading_emulator.base_trading_emulator import ITradingEmulator
from history_tests.test_results import TestResults
from result_viewer.base_viewer import IResultViewer

__all__ = ("HistoryTestsManager")

logger = logging.getLogger(__name__)


class HistoryTestsManager:
    """
    The manager for testing strategy on historical data
    """

    def __init__(
            self,
            trading_emulators: list[ITradingEmulator],
            result_viewers: list[IResultViewer]
    ) -> None:
        self.__trading_emulators = trading_emulators
        self.__result_viewers = result_viewers

    def test(
            self,
            from_days
    ) -> None:
        """
        Main entry point to start testing
        """
        logger.info(f"Start strategy tests")
        test_results: dict[str, TestResults] = dict()

        # test strategy in different emulators
        for trading_emulator in self.__trading_emulators:
            try:
                test_results[str(trading_emulator)] = trading_emulator.emulate_trading(from_days)
            except Exception as ex:
                logger.error(f"Testing error: {repr(ex)}")
            else:
                logger.info("End strategy tests")

        # Show all results
        logger.info(f"Start view all test results")
        for result_viewer in self.__result_viewers:
            try:
                result_viewer.view(test_results)
            except Exception as ex:
                logger.error(f"View results {result_viewer} error: {repr(ex)}")
