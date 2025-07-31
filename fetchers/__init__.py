"""Collection of available price fetchers."""

from .base import PriceFetcher
from .dummy_fetcher import DummyFetcher

try:
    from .data912_fetcher import Data912Fetcher
except Exception:  # pragma: no cover - optional dependency
    Data912Fetcher = None

try:
    from .banco_piano_fetcher import BancoPianoFetcher
except Exception:  # pragma: no cover - optional dependency
    BancoPianoFetcher = None

try:
    from .yfinance_fetcher import YFinanceFetcher
except Exception:  # pragma: no cover - optional dependency
    YFinanceFetcher = None

__all__ = [
    "PriceFetcher",
    "DummyFetcher",
    "YFinanceFetcher",
    "BancoPianoFetcher",
    "Data912Fetcher",
]
