import io
import logging
import re
import requests
import pandas as pd
import warnings
from datetime import date
from typing import List, Optional, Tuple

from .base import PriceFetcher

logger = logging.getLogger(__name__)


class BancoPianoFetcher(PriceFetcher):
    """Fetch bond prices from Banco Piano."""

    #: Banco Piano solo publica precios de bonos
    supported_ticker_types = ("bonos",)

    URL = "https://www.bancopiano.com.ar/Inversiones/Cotizaciones/Bonos/"

    def __init__(self) -> None:
        self._df = None

    def _load_dataframe(self) -> None:
        if self._df is not None:
            return

        attempts = 0
        while attempts < 3:
            try:
                resp = requests.get(self.URL)
                resp.raise_for_status()
                tables = pd.read_html(io.StringIO(resp.text))
                self._df = tables[0] if tables else None
                if self._df is not None and not self._df.empty:
                    break
            except requests.RequestException:
                # Connection error, retry
                self._df = None
            except Exception:
                self._df = None
                break
            attempts += 1

    def get_price(self, ticker: str, ticker_type: Optional[str] = None) -> Optional[float]:
        if ticker_type not in {None, "bonos"}:
            return None
        self._load_dataframe()
        if self._df is None or self._df.empty:
            return None
        ticker = ticker.upper()
        try:
            mask = self._df.iloc[:, 0].astype(str).str.contains(ticker, case=False, na=False)
            row = self._df.loc[mask]
            if row.empty:
                logger.debug("No se encontró fila para el ticker %s", ticker)
                return None
            # buscar columna con el precio de referencia ("Venta" o "Último")
            venta_col = None
            patterns = [
                r"VENTA\s*T\+?2",
                r"VENTA",
                r"ÚLTIMO",
                r"ULTIMO",
            ]
            for pattern in patterns:
                for col in self._df.columns:
                    if re.search(pattern, str(col), re.IGNORECASE):
                        venta_col = col
                        break
                if venta_col is not None:
                    break
            if venta_col is None:
                logger.debug("No se encontró columna de venta en la tabla")
                return None
            value = str(row.iloc[0][venta_col])
            value = value.replace(".", "").replace(",", ".")
            return float(value)
        except Exception:
            return None

    def get_history(self, ticker: str, start: date, end: date) -> List[Tuple[date, float]]:
        """Historical data not supported for this source."""
        warnings.warn("BancoPianoFetcher does not provide historical data", stacklevel=2)
        return []
