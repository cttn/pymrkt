from pathlib import Path
import sqlite3
from datetime import date
from typing import Optional, List, Tuple

DB_FILE = Path(__file__).resolve().parent / "historical.db"


def init_db() -> None:
    """Create the historical prices table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            price REAL NOT NULL,
            adj_price REAL,
            volume INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


def insert_record(ticker: str, d: date, price: float, adj_price: float, volume: int) -> None:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO history (ticker, date, price, adj_price, volume)
        VALUES (?, ?, ?, ?, ?)
        """,
        (ticker.upper(), d.isoformat(), price, adj_price, volume),
    )
    conn.commit()
    conn.close()


def get_history(ticker: str, start: date, end: date) -> List[Tuple[date, float, Optional[float], Optional[int]]]:
    """Return historical price records for ``ticker`` between ``start`` and ``end``.

    Results are ordered by date ascending and include price, adjusted price and
    volume when available.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        SELECT date, price, adj_price, volume
        FROM history
        WHERE ticker = ? AND date BETWEEN ? AND ?
        ORDER BY date ASC
        """,
        (ticker.upper(), start.isoformat(), end.isoformat()),
    )
    rows = c.fetchall()
    conn.close()
    return [
        (
            date.fromisoformat(row[0]),
            float(row[1]),
            float(row[2]) if row[2] is not None else None,
            int(row[3]) if row[3] is not None else None,
        )
        for row in rows
    ]
