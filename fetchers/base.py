from abc import ABC, abstractmethod
from typing import Optional


class PriceFetcher(ABC):
    """Interface for price fetchers."""

    @abstractmethod
    def get_price(self, ticker: str, ticker_type: Optional[str] = None) -> Optional[float]:
        """Return latest price for ``ticker`` or ``None`` if not available.

        ``ticker_type`` allows fetchers to adjust the query depending on the
        type of asset (e.g. ``"acciones"`` or ``"cedears"``). Unsupported
        types should return ``None``.
        """
        raise NotImplementedError
