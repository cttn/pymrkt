from fastapi import FastAPI, HTTPException

from config import get_lock_minutes
from fetchers import YFinanceFetcher, DummyFetcher
from .live import get_live_price

app = FastAPI()

try:
    fetcher = YFinanceFetcher() if YFinanceFetcher is not None else DummyFetcher()
except Exception:
    fetcher = DummyFetcher()


@app.get("/price/{ticker}")
def price_endpoint(ticker: str):
    price = get_live_price(ticker, fetcher, lock_minutes=get_lock_minutes())
    if price is None:
        raise HTTPException(status_code=404, detail="Price not available")
    return {"ticker": ticker.upper(), "price": price}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

