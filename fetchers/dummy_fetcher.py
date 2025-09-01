from typing import List, Optional, Tuple
from datetime import date
import random
import warnings

from .base import PriceFetcher


class DummyFetcher(PriceFetcher):
    """Return a random price for testing purposes."""

    #: Acepta cualquier tipo de ticker para fines de prueba
    supported_ticker_types = (None, "acciones", "cedears", "bonos")

    def get_price(self, ticker: str, ticker_type: Optional[str] = None) -> Optional[float]:
        return round(random.uniform(1, 100), 2)

    def get_history(self, ticker: str, start: date, end: date) -> List[Tuple[date, float]]:
        """Historical data not supported for the dummy fetcher."""
        warnings.warn("DummyFetcher does not provide historical data", stacklevel=2)
        return []
