import enum
from dataclasses import dataclass, field
from decimal import Decimal

__all__ = ("Signal", "SignalType")


@enum.unique
class SignalType(enum.IntEnum):
    LONG = 0
    SHORT = 1
    CLOSE = 2


@dataclass(eq=False, repr=True)
class Signal:
    figi: str = ""
    signal_type: SignalType = SignalType.LONG
    take_profit_level: Decimal = field(default_factory=Decimal)
    stop_loss_level: Decimal = field(default_factory=Decimal)
