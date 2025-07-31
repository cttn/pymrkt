import logging
from datetime import date, datetime
from typing import List, Optional, Tuple

import requests

from storage import live as live_db

from .base import PriceFetcher

logger = logging.getLogger(__name__)


class Data912Fetcher(PriceFetcher):
    """Fetch Argentine bond prices from the public Data912 API."""

    #: Data912 provides only bonds prices
    supported_ticker_types = ("bonos",)

    URL = "https://data912.com/live/arg_bonds"

    def get_price(
        self, ticker: str, ticker_type: Optional[str] = None
    ) -> Optional[float]:
        """Return last traded price for ``ticker`` using Data912.

        All retrieved bonds are stored in ``live.bonos.db`` for reuse.
        """
        if ticker_type != "bonos":
            return None

        try:
            resp = requests.get(self.URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.debug("Data912 request failed: %s", exc)
            return None

        if not isinstance(data, list):
            return None

        now = datetime.utcnow()
        db_file = live_db.get_db_file("bonos")
        result_price = None

        for item in data:
            symbol = item.get("symbol")
            close = item.get("c")
            if symbol is None or close is None:
                continue
            try:
                price = float(close)
            except Exception:  # noqa: BLE001
                continue
            live_db.upsert_price(symbol, price, timestamp=now, db_file=db_file)
            if symbol == ticker:
                result_price = price

        return result_price

    def get_history(
        self, ticker: str, start: date, end: date
    ) -> List[Tuple[date, float]]:
        """Historical data is not supported for Data912."""
        return []
