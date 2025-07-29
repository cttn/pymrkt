from pathlib import Path
import sqlite3
from datetime import date
from typing import Optional

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
