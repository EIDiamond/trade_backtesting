from decimal import Decimal
from dataclasses import dataclass, field

__all__ = ("StrategySettings", "CommissionSettings")


@dataclass(eq=False, repr=True)
class StrategySettings:
    name: str = ""
    figi: str = ""
    ticker: str = ""
    max_lots_per_order: int = 1
    # All internal strategy settings are represented as dict. A strategy class have to parse it himself.
    # Here, we avoid any strong dependencies and obligations
    settings: dict = field(default_factory=dict)
    lot_size: int = 1
    short_enabled_flag: bool = True


@dataclass(eq=False, repr=True)
class CommissionSettings:
    every_order: Decimal = field(default_factory=Decimal)
