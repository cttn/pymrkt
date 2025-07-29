from datetime import datetime, timedelta
from typing import Optional

from fetchers import PriceFetcher
from storage import live as live_db


def get_live_price(ticker: str, fetcher: PriceFetcher, lock_minutes: int = 15) -> Optional[float]:
    """Return up-to-date price for ticker using the provided fetcher."""
    record = live_db.get_price(ticker)
    now = datetime.utcnow()

    if record:
        price, updated_at = record
        if now - updated_at < timedelta(minutes=lock_minutes):
            return price
    else:
        price = None

    new_price = fetcher.get_price(ticker)
    if new_price is not None:
        live_db.upsert_price(ticker, new_price, now)
        return new_price

    # If fetching failed and we had an old price, return it
    return price
