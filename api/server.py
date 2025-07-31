from fastapi import FastAPI, HTTPException

from config import get_lock_minutes, get_server_host, get_server_port
from fetchers import (
    BancoPianoFetcher,
    Data912Fetcher,
    DolarApiFetcher,
    DummyFetcher,
    YFinanceFetcher,
)

from .live import get_live_price

app = FastAPI()

fetchers = []
try:
    if YFinanceFetcher is not None:
        fetchers.append(YFinanceFetcher())
except Exception:
    pass

try:
    if Data912Fetcher is not None:
        fetchers.append(Data912Fetcher())
except Exception:
    pass

try:
    if DolarApiFetcher is not None:
        fetchers.append(DolarApiFetcher())
except Exception:
    pass

try:
    if BancoPianoFetcher is not None:
        fetchers.append(BancoPianoFetcher())
except Exception:
    pass

if not fetchers:
    fetchers.append(DummyFetcher())


@app.get("/price/{ticker_type}/{ticker}")
def price_with_type_endpoint(ticker_type: str, ticker: str):
    result = get_live_price(
        ticker, fetchers, lock_minutes=get_lock_minutes(), ticker_type=ticker_type
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Price not available")
    price, updated_at = result
    return {
        "ticker": ticker.upper(),
        "price": price,
        "updated_at": updated_at.isoformat() + "Z",
    }


@app.get("/bonos/{ticker}")
def bonos_endpoint(ticker: str):
    return price_with_type_endpoint("bonos", ticker)


@app.get("/price/{ticker}")
def price_endpoint(ticker: str):
    result = get_live_price(ticker, fetchers, lock_minutes=get_lock_minutes())
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
