"""Build a validated portfolio or market source for the caller to accept."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from csv_reader import InputError, read_rows
from dsa.hash_table import HashTable
from dsa.linked_queue import Queue
from models.account import Account
from models.market import MarketEvent, SourceInfo
from models.position import Position


ACCOUNT_COLUMNS = ("account_id", "account_name")
POSITION_COLUMNS = (
    "position_id", "account_id", "ticker", "quantity", "entry_price",
    "stop_loss_pct", "take_profit_pct", "trailing_stop_pct",
)
PRICE_COLUMNS = ("timestamp", "ticker", "price")


@dataclass
class Portfolio:
    accounts: HashTable
    positions: HashTable
    positions_by_ticker: HashTable


@dataclass
class MarketData:
    events: Queue
    source: SourceInfo


def required_text(text, location):
    value = text.strip()
    if not value:
        raise InputError(f"{location}: value is required")
    return value


def positive_quantity(text, location):
    try:
        if "_" in text:
            raise ValueError
        quantity = int(text)
    except ValueError as error:
        raise InputError(f"{location}: expected a positive integer, got {text!r}") from error
    if quantity <= 0:
        raise InputError(f"{location}: expected a positive integer, got {text!r}")
    return quantity


def positive_decimal(text, location):
    try:
        if "_" in text:
            raise InvalidOperation
        value = Decimal(text.strip())
    except InvalidOperation as error:
        raise InputError(f"{location}: expected a decimal number, got {text!r}") from error
    if not value.is_finite() or value <= 0:
        raise InputError(f"{location}: expected a finite number greater than zero, got {text!r}")
    return value


def rule_percent(text, location, upper_limit=None):
    if not text.strip():
        return None
    value = positive_decimal(text, location)
    if upper_limit is not None and value >= upper_limit:
        raise InputError(f"{location}: percentage must be less than {upper_limit}, got {text!r}")
    return value


def load_portfolio(account_path, position_path):
    """P1. Build all three indexes from the two files before returning them."""
    accounts = HashTable()
    positions = HashTable()
    positions_by_ticker = HashTable()

    for line, row in read_rows(account_path, ACCOUNT_COLUMNS):
        location = f"{account_path}: line {line}"
        account_id = required_text(row["account_id"], f"{location}, account_id")
        if account_id in accounts:
            raise InputError(f"{location}, account_id: duplicate ID {account_id!r}")

        account_name = row["account_name"].strip()
        if not account_name:
            account_name = account_id
        account = Account(account_id, account_name)
        accounts.set(account_id, account)

    for line, row in read_rows(position_path, POSITION_COLUMNS):
        location = f"{position_path}: line {line}"
        position_id = required_text(row["position_id"], f"{location}, position_id")
        if position_id in positions:
            raise InputError(f"{location}, position_id: duplicate ID {position_id!r}")
        account_id = required_text(row["account_id"], f"{location}, account_id")
        if account_id not in accounts:
            raise InputError(f"{location}, account_id: account {account_id!r} does not exist")

        ticker = required_text(row["ticker"], f"{location}, ticker").upper()
        quantity = positive_quantity(row["quantity"], f"{location}, quantity")
        entry_price = positive_decimal(row["entry_price"], f"{location}, entry_price")
        stop_loss_pct = rule_percent(row["stop_loss_pct"], f"{location}, stop_loss_pct", 100)
        take_profit_pct = rule_percent(row["take_profit_pct"], f"{location}, take_profit_pct")
        trailing_stop_pct = rule_percent(row["trailing_stop_pct"], f"{location}, trailing_stop_pct", 100)

        position = Position(
            position_id=position_id,
            account_id=account_id,
            ticker=ticker,
            quantity=quantity,
            entry_price=entry_price,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            trailing_stop_pct=trailing_stop_pct,
        )
        positions.set(position_id, position)

        # The ticker group stores the same position object as the ID table.
        ticker_positions = positions_by_ticker.get(ticker)
        if ticker_positions is None:
            ticker_positions = []
            positions_by_ticker.set(ticker, ticker_positions)
        ticker_positions.append(position)

    return Portfolio(accounts, positions, positions_by_ticker)


def parse_timestamp(text, location):
    try:
        timestamp = datetime.fromisoformat(text.strip())
    except ValueError as error:
        raise InputError(f"{location}: expected an ISO 8601 timestamp, got {text!r}") from error
    if timestamp.utcoffset() != timedelta(hours=7):
        raise InputError(f"{location}: expected a +07:00 offset, got {text!r}")
    return timestamp


def load_market_prices(price_path):
    """P2. Validate file order and enqueue each market event in that order."""
    events = Queue()
    prices_by_event = {}
    tickers = set()
    first_timestamp = None
    last_timestamp = None

    for line, row in read_rows(price_path, PRICE_COLUMNS):
        location = f"{price_path}: line {line}"
        timestamp = parse_timestamp(row["timestamp"], f"{location}, timestamp")
        ticker = required_text(row["ticker"], f"{location}, ticker").upper()
        price = positive_decimal(row["price"], f"{location}, price")

        if last_timestamp is not None and timestamp < last_timestamp:
            raise InputError(f"{location}, timestamp: earlier than the preceding event")
        event_key = (timestamp, ticker)
        if event_key in prices_by_event:
            if prices_by_event[event_key] == price:
                problem = "duplicate event"
            else:
                problem = "conflicting price"
            raise InputError(f"{location}, timestamp/ticker: {problem} for {ticker} at {timestamp.isoformat()}")

        event = MarketEvent(timestamp, ticker, price)
        events.enqueue(event)
        prices_by_event[event_key] = price
        tickers.add(ticker)
        if first_timestamp is None:
            first_timestamp = timestamp
        last_timestamp = timestamp

    if events.is_empty():
        raise InputError(f"{price_path}: expected at least one price event")

    source = SourceInfo(
        str(price_path), len(events), tuple(sorted(tickers)), first_timestamp, last_timestamp,
    )
    return MarketData(events, source)
