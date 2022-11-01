from dataclasses import dataclass
from datetime import datetime

from tinkoff.invest import Quotation


@dataclass(eq=True, repr=True)
class InternalCandle:
    open: Quotation
    high: Quotation
    low: Quotation
    close: Quotation
    volume: int
    time: datetime
