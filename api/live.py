from datetime import datetime, timedelta
from typing import Optional, Tuple, Iterable, Union, List
from statistics import median

from config import get_lock_minutes

from fetchers import PriceFetcher
from storage import live as live_db


def get_live_price(
    ticker: str,
    fetcher: Union[PriceFetcher, Iterable[PriceFetcher]],
    lock_minutes: Optional[int] = None,
    debug: bool = False,
    ticker_type: Optional[str] = None,
) -> Optional[Tuple[float, datetime]]:
    """Return up-to-date price and timestamp for ``ticker``.

    ``ticker_type`` selects the database to use and may influence the
    fetcher behaviour.
    """
    if lock_minutes is None:
        lock_minutes = get_lock_minutes()
    db_file = live_db.get_db_file(ticker_type)
    record = live_db.get_price(ticker, db_file=db_file)
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

    if isinstance(fetcher, PriceFetcher):
        fetchers: List[PriceFetcher] = [fetcher]
    else:
        fetchers = list(fetcher)

    # Only use fetchers that support the requested ticker type
    if ticker_type is None:
        fetchers = [
            f
            for f in fetchers
            if None in getattr(f, "supported_ticker_types", (None,))
        ]
    else:
        fetchers = [
            f
            for f in fetchers
            if ticker_type in getattr(f, "supported_ticker_types", ())
        ]

    prices = []
    for f in fetchers:
        p = f.get_price(ticker, ticker_type)
        if p is not None:
            prices.append(p)
            if debug:
                print(f"[DEBUG] {ticker}: fetched price from {f.__class__.__name__}")

    if prices:
        new_price = median(prices)
        live_db.upsert_price(ticker, new_price, now, db_file=db_file)
        return new_price, now

    # If fetching failed and we had an old price, return it
    if debug and price is not None:
        print(f"[DEBUG] {ticker}: fetch failed, returning cached price")
    if price is not None:
        return price, updated_at
    return None
