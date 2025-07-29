from datetime import datetime, timedelta
from typing import Optional, Tuple

from config import get_lock_minutes

from fetchers import PriceFetcher
from storage import live as live_db


def get_live_price(
    ticker: str,
    fetcher: PriceFetcher,
    lock_minutes: Optional[int] = None,
    debug: bool = False,
) -> Optional[Tuple[float, datetime]]:
    """Return up-to-date price and timestamp for ``ticker``."""
    if lock_minutes is None:
        lock_minutes = get_lock_minutes()
    record = live_db.get_price(ticker)
    now = datetime.utcnow()

    if record:
        price, updated_at = record
        if now - updated_at < timedelta(minutes=lock_minutes):
            if debug:
                print(f"[DEBUG] {ticker}: using cached price from DB")
            return price, updated_at
    else:
        price = None
        updated_at = None

    new_price = fetcher.get_price(ticker)
    if new_price is not None:
        live_db.upsert_price(ticker, new_price, now)
        if debug:
            print(
                f"[DEBUG] {ticker}: fetched price from {fetcher.__class__.__name__}"
            )
        return new_price, now

    # If fetching failed and we had an old price, return it
    if debug and price is not None:
        print(f"[DEBUG] {ticker}: fetch failed, returning cached price")
    if price is not None:
        return price, updated_at
    return None
