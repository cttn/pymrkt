"""Collection of available price fetchers."""

from .base import PriceFetcher
from .dummy_fetcher import DummyFetcher

try:
    from .yfinance_fetcher import YFinanceFetcher
except Exception:  # pragma: no cover - optional dependency
    YFinanceFetcher = None

__all__ = ["PriceFetcher", "DummyFetcher", "YFinanceFetcher"]
