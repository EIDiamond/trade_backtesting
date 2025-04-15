import logging
from decimal import Decimal

from matplotlib import pyplot as plt

from result_viewer.base_viewer import IResultViewer
from history_tests.test_results import TestResults
from trade_system.commissions.base_commission import ICommissionCalculator
from trade_system.signal import SignalType

__all__ = ("ResultViewerToPlot")

logger = logging.getLogger(__name__)


class ResultViewerToPlot(IResultViewer):
    """
    Class view test results into matplotlib view
    """

    def __init__(self, commission_calculator: ICommissionCalculator):
        self.__commission_calculator = commission_calculator

    def view(self, test_results: dict[str, TestResults]) -> None:
        """
        Just print results to plot
        """
        logger.info("Start fill the plot")

        # create main figure
        plt.figure(layout='tight')
        subplot_index = 0

        for test_results_name, test_result in test_results.items():
            logger.info(f"Prepare plot for {test_results_name}")

            subplot_index += 1
            profit = Decimal(0)
            total_commission = Decimal(0)

            # create subplot for current test_results_name
            plt.subplot(len(test_results), 1, subplot_index)

            for test_order in test_result.executed_orders:
                total_commission += self.__commission_calculator.calculate(test_order.open_level) + \
                                    self.__commission_calculator.calculate(test_order.close_level)

                if test_order.signal.signal_type == SignalType.LONG:
                    # long profit if close > open
                    profit = profit + test_order.close_level - test_order.open_level
                else:
                    # short profit if open > close
                    profit = profit + test_order.open_level - test_order.close_level

            # show results as bar with profit, commission and summary
            plt.bar(["profit", "commission", "summary"], [profit, (-1) * total_commission, profit - total_commission])
            plt.title(f"Test result: {test_results_name}")
            plt.grid(True)

        logger.info("Show plot with results")

        plt.show()
