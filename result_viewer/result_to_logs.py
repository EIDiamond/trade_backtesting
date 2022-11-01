import logging
from decimal import Decimal

from result_viewer.base_viewer import IResultViewer
from history_tests.test_results import TestResults
from trade_system.commissions.base_commission import ICommissionCalculator
from trade_system.signal import SignalType

__all__ = ("ResultViewerToLogs")

logger = logging.getLogger(__name__)


class ResultViewerToLogs(IResultViewer):
    """
    Class view test results into log file
    """

    def __init__(self, commission_calculator: ICommissionCalculator):
        self.__commission_calculator = commission_calculator

    def view(self, test_results: dict[str, TestResults]) -> None:
        """
        Just print results to log file
        """
        logger.info("Test Results section:")

        for test_results_name, test_result in test_results.items():
            logger.info(f"Test Results: {test_results_name}")

            if test_result.current_position:
                logger.info(f"Current Signal: {test_result.current_position.signal}")
            else:
                logger.info(f"Current Signal is empty")

            profit = Decimal(0)
            total_commission = Decimal(0)
            take_profit_count = 0

            for test_order in test_result.executed_orders:
                profit_result = (
                                        test_order.open_level < test_order.close_level and test_order.signal.signal_type == SignalType.LONG
                                ) or (
                                        test_order.open_level > test_order.close_level and test_order.signal.signal_type == SignalType.SHORT
                                )
                if profit_result:
                    take_profit_count += 1

                logger.info(f"Executed order. {test_order.signal}.")
                logger.info(f"Order profit result: {profit_result}.")
                logger.info(f"Open: {test_order.open_level}; Close: {test_order.close_level}")

                commission = self.__commission_calculator.calculate(test_order.open_level) + \
                             self.__commission_calculator.calculate(test_order.open_level)
                total_commission += commission
                logger.info(f"Commission: {commission}")

                if test_order.signal.signal_type == SignalType.LONG:
                    # long profit if close > open
                    profit = profit + test_order.close_level - test_order.open_level
                else:
                    # short profit if open > close
                    profit = profit + test_order.open_level - test_order.close_level

            logger.info(f"Signals executed: {len(test_result.executed_orders)}")
            logger.info(f"Take Profit: {take_profit_count}")
            logger.info(f"Stop Loss: {len(test_result.executed_orders) - take_profit_count}")

            logger.info(f"Total trade profit: {profit}")
            logger.info(f"Total commission: {total_commission}")
            logger.info(f"Total trade summary: {profit - total_commission}")
