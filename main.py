"""Minimal entry point for pymrkt."""

import argparse

from fetchers import YFinanceFetcher
from api import get_live_price
from config import get_lock_minutes
from storage import live as live_db
from scripts import init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Run pymrkt")
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug output"
    )
    args = parser.parse_args()

    init_db.main()
    fetcher = YFinanceFetcher()
    lock_minutes = get_lock_minutes()

    tickers = live_db.list_tickers()
    for ticker in tickers:
        result = get_live_price(
            ticker, fetcher, lock_minutes=lock_minutes, debug=args.debug
        )
        if result is None:
            print(ticker, "N/A")
        else:
            price, updated_at = result
            print(ticker, price, updated_at.isoformat() + "Z")


if __name__ == "__main__":
    main()
