import logging
from typing import List, Optional, Tuple

import requests
import warnings
from datetime import date

from .base import PriceFetcher

logger = logging.getLogger(__name__)


class DolarApiFetcher(PriceFetcher):
    """Fetch USD price from dolarapi.com."""

    #: Supports only USD under ticker type "monedas"
    supported_ticker_types = ("monedas",)

    URL = "https://dolarapi.com/v1/dolares/bolsa"

    def get_price(
        self, ticker: str, ticker_type: Optional[str] = None
    ) -> Optional[float]:
        if ticker_type != "monedas" or ticker.upper() != "USD":
            return None
        try:
            resp = requests.get(self.URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            compra = data.get("compra")
            venta = data.get("venta")
            if compra is None or venta is None:
                return None
            avg = (float(compra) + float(venta)) / 2
            return round(avg, 2)
        except Exception as exc:  # noqa: BLE001
            logger.debug("dolarapi request failed: %s", exc)
            return None

    def get_history(self, ticker: str, start: date, end: date) -> List[Tuple[date, float]]:
        """Historical data not provided by this API."""
        warnings.warn("DolarApiFetcher does not provide historical data", stacklevel=2)
        return []
