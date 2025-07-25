import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://api.binance.com"

def get_all_symbols():
    url = f"{BASE_URL}/api/v3/exchangeInfo"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "symbols" not in data:
            return ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # fallback
        symbols = [s['symbol'] for s in data['symbols'] if s['quoteAsset'] == 'USDT']
        return symbols
    except Exception as e:
        return ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # fallback se der erro
