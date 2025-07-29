from typing import Optional
import yfinance as yf

from .base import PriceFetcher


class YFinanceFetcher(PriceFetcher):
    """Fetch prices using yfinance."""

    def get_price(self, ticker: str) -> Optional[float]:
        try:
            data = yf.Ticker(ticker)
            price = data.info.get("regularMarketPrice")
            return float(price) if price is not None else None
        except Exception:
            return None
