import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union

BASE_PATH = Path(__file__).resolve().parent

DEFAULT_DB_FILE = BASE_PATH / "live.db"
ACCIONES_DB_FILE = BASE_PATH / "live.acciones.db"
CEDEARS_DB_FILE = BASE_PATH / "live.cedears.db"
BONOS_DB_FILE = BASE_PATH / "live.bonos.db"
MONEDAS_DB_FILE = BASE_PATH / "live.monedas.db"


def get_db_file(ticker_type: Optional[str] = None) -> Path:
    """Return the database file corresponding to ``ticker_type``."""
    if ticker_type == "acciones":
        return ACCIONES_DB_FILE
    if ticker_type == "cedears":
        return CEDEARS_DB_FILE
    if ticker_type == "bonos":
        return BONOS_DB_FILE
    if ticker_type == "monedas":
        return MONEDAS_DB_FILE
    return DEFAULT_DB_FILE


def _init_table(db_file: Union[str, Path]) -> None:
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            ticker TEXT PRIMARY KEY,
            price REAL NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def init_db() -> None:
    """Create the live price tables if they don't exist."""
    for db in [
        DEFAULT_DB_FILE,
        ACCIONES_DB_FILE,
        CEDEARS_DB_FILE,
        BONOS_DB_FILE,
        MONEDAS_DB_FILE,
    ]:
        _init_table(db)


def get_price(
    ticker: str, db_file: Optional[Union[str, Path]] = None
) -> Optional[Tuple[float, datetime]]:
    """Return price and timestamp for ticker if available."""
    if db_file is None:
        db_file = DEFAULT_DB_FILE
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        "SELECT price, updated_at FROM prices WHERE ticker = ?",
        (ticker.upper(),),
    )
    row = c.fetchone()
    conn.close()
    if row:
        price, ts = row
        return price, datetime.fromisoformat(ts)
    return None


def list_tickers(db_file: Optional[Union[str, Path]] = None) -> List[str]:
    """Return all tickers currently stored in the database."""
    if db_file is None:
        db_file = DEFAULT_DB_FILE
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT ticker FROM prices")
    tickers = [r[0] for r in c.fetchall()]
    conn.close()
    return tickers


def upsert_price(
    ticker: str,
    price: float,
    timestamp: Optional[datetime] = None,
    db_file: Optional[Union[str, Path]] = None,
) -> None:
    """Insert or update price for ticker."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    if db_file is None:
        db_file = DEFAULT_DB_FILE
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO prices (ticker, price, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(ticker) DO UPDATE SET price=excluded.price, updated_at=excluded.updated_at
        """,
        (ticker.upper(), price, timestamp.isoformat()),
    )
    conn.commit()
    conn.close()
