from pathlib import Path
import sqlite3
from datetime import datetime
from typing import Optional, Tuple

DB_FILE = Path(__file__).resolve().parent / "live.db"


def init_db() -> None:
    """Create the live prices table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
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


def get_price(ticker: str) -> Optional[Tuple[float, datetime]]:
    """Return price and timestamp for ticker if available."""
    conn = sqlite3.connect(DB_FILE)
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


def upsert_price(ticker: str, price: float, timestamp: Optional[datetime] = None) -> None:
    """Insert or update price for ticker."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    conn = sqlite3.connect(DB_FILE)
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
