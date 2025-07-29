from typing import Optional
import random

from .base import PriceFetcher


class DummyFetcher(PriceFetcher):
    """Return a random price for testing purposes."""

    #: Acepta cualquier tipo de ticker para fines de prueba
    supported_ticker_types = (None, "acciones", "cedears", "bonos")

    def get_price(self, ticker: str, ticker_type: Optional[str] = None) -> Optional[float]:
        return round(random.uniform(1, 100), 2)
