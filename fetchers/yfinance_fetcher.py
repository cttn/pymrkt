from typing import Optional
import yfinance as yf

from .base import PriceFetcher


class YFinanceFetcher(PriceFetcher):
    """Fetch prices using yfinance."""

    #: Admite acciones, CEDEARs y consultas sin tipo especificado
    supported_ticker_types = (None, "acciones", "cedears")

    def get_price(self, ticker: str, ticker_type: Optional[str] = None) -> Optional[float]:
        if ticker_type in {"acciones", "cedears"}:
            ticker = f"{ticker}.BA"
        elif ticker_type not in {None, "acciones", "cedears"}:
            # Unsupported ticker type
            return None

        try:
            data = yf.Ticker(ticker)
            price = data.info.get("regularMarketPrice")
            return float(price) if price is not None else None
        except Exception:
            return None
