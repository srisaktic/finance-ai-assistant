import yfinance as yf


def get_stock_price(ticker: str) -> dict:
    """Fetch current stock price and key stats for a given ticker."""
    stock = yf.Ticker(ticker)
    info = stock.fast_info

    return {
        "ticker": ticker,
        "current_price": round(info["lastPrice"], 2),
        "previous_close": round(info["previousClose"], 2),
        "day_high": round(info["dayHigh"], 2),
        "day_low": round(info["dayLow"], 2),
        "year_high": round(info["yearHigh"], 2),
        "year_low": round(info["yearLow"], 2),
        "year_change_pct": round(info["yearChange"] * 100, 2),
        "market_cap": info["marketCap"],
        "currency": info["currency"],
    }


if __name__ == "__main__":
    print(get_stock_price("AAPL"))