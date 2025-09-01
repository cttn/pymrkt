from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional, Tuple


class PriceFetcher(ABC):
    """Interface for price fetchers.

    Subclasses should define :pyattr:`supported_ticker_types` listing the
    ``ticker_type`` values they can handle. ``None`` indicates that the fetcher
    supports queries where no ticker type was specified.
    """

    #: Tuple of supported ticker types. ``None`` means "no type provided".
    supported_ticker_types: tuple[Optional[str], ...] = (None,)

    @abstractmethod
    def get_price(self, ticker: str, ticker_type: Optional[str] = None) -> Optional[float]:
        """Return latest price for ``ticker`` or ``None`` if not available.

        ``ticker_type`` allows fetchers to adjust the query depending on the
        type of asset (e.g. ``"acciones"`` or ``"cedears"``). Unsupported
        types should return ``None``.
        """
        raise NotImplementedError

    @abstractmethod
    def get_history(self, ticker: str, start: date, end: date) -> List[Tuple[date, float]]:
        """Return historical prices for ``ticker`` between ``start`` and ``end``.

        Subclasses that do not implement historical queries should return an
        empty list and issue a warning.
        """
        raise NotImplementedError
