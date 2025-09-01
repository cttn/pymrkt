from datetime import date
from typing import List, Dict

from storage import historical as historical_db


def get_historical_prices(ticker: str, start: date, end: date) -> List[Dict[str, object]]:
    """Return historical prices for ``ticker`` between ``start`` and ``end``.

    The data is fetched from the historical storage and serialised to JSON-
    friendly dictionaries.
    """
    records = historical_db.get_history(ticker, start, end)
    return [
        {
            "date": d.isoformat(),
            "price": price,
            "adj_price": adj_price,
            "volume": volume,
        }
        for d, price, adj_price, volume in records
    ]
