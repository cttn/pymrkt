from datetime import date
from typing import List, Optional, Tuple
import warnings
import yfinance as yf

from .base import PriceFetcher
from storage import historical


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

    def get_history(self, ticker: str, start: date, end: date) -> List[Tuple[date, float]]:
        """Retrieve and store historical prices for ``ticker`` from yfinance."""

        try:
            history_df = yf.Ticker(ticker).history(start=start, end=end)
        except Exception:
            warnings.warn("yfinance request for historical data failed", stacklevel=2)
            return []

        results: List[Tuple[date, float]] = []
        for idx, row in history_df.iterrows():
            d = idx.date()
            price = float(row.get("Close", float("nan")))
            if price != price:  # NaN check
                continue
            adj_price = row.get("Adj Close")
            volume = row.get("Volume")
            historical.insert_record(
                ticker,
                d,
                price,
                float(adj_price) if adj_price == adj_price else price,
                int(volume) if volume == volume else 0,
            )
            results.append((d, price))
        return results
