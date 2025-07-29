"""Minimal entry point for pymrkt."""

from fetchers import DummyFetcher
from api import get_live_price
from scripts import init_db


def main() -> None:
    init_db.main()
    fetcher = DummyFetcher()

    for ticker in ["AAPL", "MSFT", "GGAL"]:
        price = get_live_price(ticker, fetcher, lock_minutes=30)
        print(ticker, price)


if __name__ == "__main__":
    main()
