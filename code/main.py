"""English terminal menu for the P1–P3 midterm demo."""

import sys
from pathlib import Path

from csv_reader import InputError
from loaders import load_market_prices, load_portfolio
from views import show_accounts, show_positions, show_price_source


SAMPLES_DIR = Path(__file__).resolve().parent / "samples"


def ask_path(filename):
    entered = input(f"Path to {filename} [Enter for the sample]: ").strip().strip('"')
    if entered:
        return Path(entered)
    return SAMPLES_DIR / filename


def warn_missing_prices(portfolio, source):
    if portfolio is None or source is None:
        return

    available_tickers = set(source.tickers)
    missing_tickers = []
    for ticker, _ in portfolio.positions_by_ticker.items():
        if ticker not in available_tickers:
            missing_tickers.append(ticker)

    if missing_tickers:
        missing_tickers.sort()
        print(f"Warning: no market prices for held tickers {', '.join(missing_tickers)}.")


def view_current_data(portfolio, source):
    while True:
        print("\nVIEW CURRENT DATA")
        print("1. List accounts")
        print("2. View positions by account")
        print("3. View price source")
        print("0. Back")
        choice = input("Choose an option: ").strip()

        if choice == "0":
            return
        if choice == "1":
            show_accounts(portfolio)
        elif choice == "2":
            if portfolio is None:
                print("Load a portfolio first.")
            else:
                account_id = input("Account ID: ").strip()
                show_positions(portfolio, account_id)
        elif choice == "3":
            show_price_source(source)
        else:
            print("Invalid option. Choose 0, 1, 2, or 3.")


def main():
    portfolio = None
    market = None

    while True:
        print("\nMULTI-USER STOCK TRADE MANAGEMENT SYSTEM")
        print("1. Load portfolio from CSV")
        print("2. Load market prices from CSV")
        print("3. View current data")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            return

        try:
            if choice == "1":
                account_path = ask_path("accounts.csv")
                position_path = ask_path("positions.csv")
                portfolio = load_portfolio(account_path, position_path)
                account_count = len(portfolio.accounts)
                position_count = len(portfolio.positions)
                print(f"Portfolio loaded: {account_count} accounts, {position_count} positions.")
                warn_missing_prices(portfolio, market.source if market else None)
            elif choice == "2":
                price_path = ask_path("prices.csv")
                market = load_market_prices(price_path)
                print("Market prices loaded.")
                show_price_source(market.source)
                warn_missing_prices(portfolio, market.source)
            elif choice == "3":
                view_current_data(portfolio, market.source if market else None)
            else:
                print("Invalid option. Choose 0, 1, 2, or 3.")
        except InputError as error:
            print(f"Load rejected. {error}")
            print("The previously loaded data is still available.")


if __name__ == "__main__":
    # Redirected Windows output may use an encoding that cannot display a CSV path or name.
    sys.stdout.reconfigure(errors="backslashreplace")
    try:
        main()
    except EOFError:
        print("\nGoodbye.")
