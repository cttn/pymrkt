from fastapi import FastAPI, HTTPException

from config import get_lock_minutes, get_server_host, get_server_port
from fetchers import YFinanceFetcher, DummyFetcher
from .live import get_live_price

app = FastAPI()

try:
    fetcher = YFinanceFetcher() if YFinanceFetcher is not None else DummyFetcher()
except Exception:
    fetcher = DummyFetcher()


@app.get("/price/{ticker}")
def price_endpoint(ticker: str):
    result = get_live_price(ticker, fetcher, lock_minutes=get_lock_minutes())
    if result is None:
        raise HTTPException(status_code=404, detail="Price not available")
    price, updated_at = result
    return {
        "ticker": ticker.upper(),
        "price": price,
        "updated_at": updated_at.isoformat() + "Z",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=get_server_host(), port=get_server_port())

