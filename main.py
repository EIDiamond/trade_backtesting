import logging
import os
from logging.handlers import RotatingFileHandler

from configuration.configuration import ProgramConfiguration
from data_provider.data_provider_factory import DataProviderFactory
from history_tests.history_manager import HistoryTestsManager
from history_tests.trading_emulator.moving_stop_emulator import MovingStopEmulator
from history_tests.trading_emulator.stop_take_emulator import StopTakeEmulator
from result_viewer.result_to_logs import ResultViewerToLogs
from result_viewer.result_to_plot import ResultViewerToPlot
from trade_system.commissions.commissions import CommissionEveryOrderCalculator

# the configuration file name
CONFIG_FILE = "settings.ini"

logger = logging.getLogger(__name__)


def prepare_logs() -> None:
    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        handlers=[RotatingFileHandler('logs/test.log', maxBytes=100000000, backupCount=10, encoding='utf-8')],
        encoding="utf-8"
    )


if __name__ == "__main__":
    prepare_logs()

    logger.info("Historical candles backtesting has been started.")

    try:
        config = ProgramConfiguration(CONFIG_FILE)
        logger.info("Configuration has been loaded")
    except Exception as ex:
        logger.critical("Load configuration error: %s", repr(ex))
    else:
        # create data provider
        data_provider = DataProviderFactory.new_factory(
            config.data_provider_name,
            *config.data_provider_settings
        )
        # create calculator of commissions
        commission_calculator = CommissionEveryOrderCalculator(config.commission_settings)
        # create result viewers
        result_viewers = [ResultViewerToLogs(commission_calculator), ResultViewerToPlot(commission_calculator)]
        # create trading emulators - using all available
        trading_emulators = [
            MovingStopEmulator(
                config.test_strategy_settings.name,
                config.test_strategy_settings,
                data_provider,
                True,
                True
            ),
            MovingStopEmulator(
                config.test_strategy_settings.name,
                config.test_strategy_settings,
                data_provider,
                True,
                False
            ),
            MovingStopEmulator(
                config.test_strategy_settings.name,
                config.test_strategy_settings,
                data_provider,
                False,
                True
            ),
            MovingStopEmulator(
                config.test_strategy_settings.name,
                config.test_strategy_settings,
                data_provider,
                False,
                False
            ),
            StopTakeEmulator(
                config.test_strategy_settings.name,
                config.test_strategy_settings,
                data_provider,
                True
            ),
            StopTakeEmulator(
                config.test_strategy_settings.name,
                config.test_strategy_settings,
                data_provider,
                False
            )
        ]

        # start testing
        HistoryTestsManager(trading_emulators, result_viewers).test(from_days=config.data_provider_from_days)

    logger.info("Backtesting has been ended")
