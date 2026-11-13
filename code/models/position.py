from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Position:
    """One lot, with its own entry price and optional exit rules."""

    position_id: str
    account_id: str
    ticker: str
    quantity: int
    entry_price: Decimal
    stop_loss_pct: Decimal | None = None
    take_profit_pct: Decimal | None = None
    trailing_stop_pct: Decimal | None = None
    state: str = "OPEN"
