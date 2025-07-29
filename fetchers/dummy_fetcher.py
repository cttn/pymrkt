from typing import Optional
import random

from .base import PriceFetcher


class DummyFetcher(PriceFetcher):
    """Return a random price for testing purposes."""

    def get_price(self, ticker: str) -> Optional[float]:
        return round(random.uniform(1, 100), 2)
