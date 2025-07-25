import requests
import pandas as pd
from datetime import datetime

COINGECKO_URL = "https://api.coingecko.com/api/v3"

def get_all_symbols():
    """Retorna uma lista com criptos populares (id usado pelo CoinGecko)"""
    try:
        url = f"{COINGECKO_URL}/coins/markets"
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 50, "page": 1}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [coin["id"] for coin in data]  # exemplo: "bitcoin", "ethereum"
    except:
        return ["bitcoin", "ethereum", "binancecoin"]

def get_price(coin_id):
    """Retorna preço atual em USD"""
    try:
        url = f"{COINGECKO_URL}/simple/price"
        params = {"ids": coin_id, "vs_currencies": "usd"}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return float(data[coin_id]["usd"])
    except:
        return None

def get_historical_data(coin_id, days=365):
    """Retorna histórico dos últimos X dias para forecast"""
    try:
        url = f"{COINGECKO_URL}/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": days}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        prices = data.get("prices", [])
        if not prices:
            return pd.DataFrame(columns=["ds", "y"])

        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["ds"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["y"] = df["price"]
        return df[["ds", "y"]]
    except:
        return pd.DataFrame(columns=["ds", "y"])
