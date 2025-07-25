import yfinance as yf
import pandas as pd

def get_all_symbols():
    # Principais criptos (Yahoo usa formato BTC-USD, ETH-USD etc.)
    return [
        "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD",
        "ADA-USD", "SOL-USD", "DOGE-USD", "DOT-USD",
        "MATIC-USD", "LTC-USD"
    ]

def get_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        return float(data["Close"].iloc[-1])
    except:
        return None

def get_historical_data(symbol, days=365):
    try:
        ticker = yf.Ticker(symbol)
        period = f"{days}d" if days <= 365 else "1y"
        data = ticker.history(period=period, interval="1d")

        if data.empty:
            return pd.DataFrame(columns=["ds", "y"])

        data.reset_index(inplace=True)
        df = data.rename(columns={"Date": "ds", "Close": "y"})
        return df[["ds", "y"]]
    except:
        return pd.DataFrame(columns=["ds", "y"])
