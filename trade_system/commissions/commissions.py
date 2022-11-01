from decimal import Decimal

from configuration.settings import CommissionSettings
from trade_system.commissions.base_commission import ICommissionCalculator

__all__ = ("CommissionEveryOrderCalculator")


class CommissionEveryOrderCalculator(ICommissionCalculator):
    """Commission calculator for Tinkoff broker and INVESTOR tariff"""
    def __init__(self, settings: CommissionSettings) -> None:
        self.__settings = settings

    def calculate(self, price: Decimal) -> Decimal:
        return price * self.__settings.every_order
