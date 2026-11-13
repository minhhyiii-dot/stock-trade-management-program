"""Read the loaded portfolio and market metadata for the P3 screens."""

def print_table(title, headers, rows):
    widths = [len(header) for header in headers]
    text_rows = []
    for row in rows:
        text_row = []
        for column, value in enumerate(row):
            cell = str(value).replace("\r", r"\r").replace("\n", r"\n")
            text_row.append(cell)
            widths[column] = max(widths[column], len(cell))
        text_rows.append(text_row)

    def format_row(row):
        return " | ".join(value.ljust(width) for value, width in zip(row, widths))

    print(f"\n{title}")
    print(format_row(headers))
    print("-+-".join("-" * width for width in widths))
    for row in text_rows:
        print(format_row(row))


def show_accounts(portfolio):
    if portfolio is None:
        print("Load a portfolio first.")
        return
    if len(portfolio.accounts) == 0:
        print("The loaded portfolio has no accounts.")
        return

    counts = {}
    for position in portfolio.positions.values():
        key = (position.account_id, position.state)
        counts[key] = counts.get(key, 0) + 1

    rows = []
    for account_id, account in sorted(portfolio.accounts.items()):
        open_count = counts.get((account_id, "OPEN"), 0)
        closed_count = counts.get((account_id, "CLOSED"), 0)
        rows.append((account_id, account.account_name, open_count, closed_count))
    print_table("ACCOUNTS", ("Account ID", "Name", "Open", "Closed"), rows)


def rule_text(value):
    if value is None:
        return "Off"
    return f"{value}%"


def show_positions(portfolio, account_id):
    account = portfolio.accounts.get(account_id)
    if account is None:
        print(f"Account {account_id!r} was not found.")
        return

    positions = []
    for position in portfolio.positions.values():
        if position.account_id == account_id:
            positions.append(position)
    if not positions:
        print(f"Account {account_id} has no positions.")
        return

    rows = []
    for position in sorted(positions, key=lambda position: position.position_id):
        entry_price = f"{position.entry_price:,.2f}".rstrip("0").rstrip(".")
        rows.append((
            position.position_id, position.ticker, position.quantity, entry_price,
            rule_text(position.stop_loss_pct), rule_text(position.take_profit_pct),
            rule_text(position.trailing_stop_pct), position.state,
        ))
    headers = ("Position ID", "Ticker", "Shares", "Entry (VND)", "Stop Loss", "Take Profit", "Trailing", "State")
    print_table(f"POSITIONS FOR {account.account_id} ({account.account_name})", headers, rows)


def show_price_source(source):
    if source is None:
        print("Load a market price file first.")
        return

    rows = [
        ("Total source events", source.event_count),
        ("Ticker count", len(source.tickers)),
        ("Tickers", ", ".join(source.tickers)),
        ("First timestamp", source.first_timestamp.isoformat()),
        ("Last timestamp", source.last_timestamp.isoformat()),
    ]
    print_table("PRICE SOURCE", ("Field", "Value"), rows)
    print(f"File: {source.path}")
