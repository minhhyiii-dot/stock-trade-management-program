from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class MarketEvent:
    timestamp: datetime
    ticker: str
    price: Decimal


@dataclass(frozen=True)
class SourceInfo:
    path: str
    event_count: int
    tickers: tuple[str, ...]
    first_timestamp: datetime
    last_timestamp: datetime
