from abc import ABC, abstractmethod
from typing import Optional


class PriceFetcher(ABC):
    """Interface for price fetchers."""

    @abstractmethod
    def get_price(self, ticker: str) -> Optional[float]:
        """Return latest price for ticker or None if not available."""
        raise NotImplementedError
