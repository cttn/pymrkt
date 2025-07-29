"""Minimal entry point for pymrkt."""

import argparse

from fetchers import DummyFetcher
from api import get_live_price
from scripts import init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Run pymrkt")
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug output"
    )
    args = parser.parse_args()

    init_db.main()
    fetcher = DummyFetcher()

    for ticker in ["AAPL", "MSFT", "GGAL"]:
        price = get_live_price(ticker, fetcher, lock_minutes=30, debug=args.debug)
        print(ticker, price)


if __name__ == "__main__":
    main()
