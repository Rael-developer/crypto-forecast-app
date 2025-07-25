import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://api.binance.com"

def get_price(symbol):
    url = f"{BASE_URL}/api/v3/ticker/price"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, params={"symbol": symbol}, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "price" in data:
            return float(data['price'])
        else:
            # Se a resposta não contém price, significa erro
            return None
    except Exception as e:
        return None

def get_all_symbols():
    url = f"{BASE_URL}/api/v3/exchangeInfo"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "symbols" not in data:
            return ["BTC/USDT", "ETH/USDT", "BNB/USDT"]  # fallback
        symbols = [s['symbol'] for s in data['symbols'] if s['quoteAsset'] == 'USDT']
        return symbols
    except Exception as e:
        return ["BTC/USDT", "ETH/USDT", "BNB/USDT"]  # fallback se der erro
        
def get_historical_data(symbol="BTCUSDT", interval="1d", limit=500):
    url = f"{BASE_URL}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url).json()
    data = []
    for k in r:
        data.append([datetime.fromtimestamp(k[0]/1000), float(k[4])])
    df = pd.DataFrame(data, columns=['ds', 'y'])
    return df
